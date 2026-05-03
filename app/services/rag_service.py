from operator import itemgetter
from typing import List, Dict, Any
import logging

from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import get_llm, EMBEDDINGS
from app.core.prompts import RAG_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.llm = get_llm()
        self.vectorstore = PineconeVectorStore(
            index_name="documind-enterprise",
            embedding=EMBEDDINGS,
            namespace="default"
        )
        self.retriever = self.vectorstore.as_retriever(
                search_kwargs={
                    "k": 3,
                    "namespace": "default"
                    })

        # --- Stage 1: The Rephraser Contract ---
        # Added MessagesPlaceholder to ensure history is correctly formatted
        self.rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert search query generator. Analyze the chat history and the latest user question. "
               "Rewrite the question into a dense, keyword-rich standalone search query for a vector database. "
               "Focus on specific nouns and entities (like names, technologies, or document types). "
               "Return ONLY the rewritten query text. DO NOT answer it."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])       
        # --- Stage 2: The QA Contract ---
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_PROMPT_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]) 

    def _get_standalone_question(self, question: str, chat_history: List) -> str:
        """Resolves context-dependent terms like 'it', 'him', or 'then'."""
        if not chat_history:
            return question
        rephrase_chain = self.rephrase_prompt | self.llm | StrOutputParser()
        return rephrase_chain.invoke({
            "input": question,
            "chat_history": chat_history
        })

    def answer_question(self, question: str, chat_history: List) -> Dict[str, Any]:
        try: 
            # 1. Windowing: Performance & Cost Guardrail
            windowed_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

            # 2. Contextualization: Solving the 'It' Problem
            standalone_query = self._get_standalone_question(question, windowed_history)
            
            #logger.info("--- RAG TRACE ---")
            #logger.info(f"Original Question: {question}")
            #logger.info(f"Rephrased Query: {standalone_query}")

          #  retrieved_docs = self.retriever.invoke(standalone_query)
            retrieved_docs = self.retriever.invoke(standalone_query)
#            logger.info(f"Total Chunks Found: {len(retrieved_docs)}")

#            for i, doc in enumerate(retrieved_docs):
  #              logger.info(f"Chunk {i} (Source: {doc.metadata.get('source')}): {doc.page_content[:150]}...")

            if not retrieved_docs:
                return {
                        "answer": "I found your resume in the archive, but I couldn't find it",
                        "status": "partial_success",
                       # "standalone_query": standalone_query
                       "context": []
                    }
            # 3. The Enterprise RAG Chain
            # We use a dictionary mapping to ensure the 'context' is captured 
            # and that all variables in RAG_PROMPT_TEMPLATE are satisfied.
            rag_chain = (
                RunnableParallel({
                    "context": itemgetter("docs") ,#| self.retriever,
                    "chat_history": itemgetter("chat_history"),
                    "input": itemgetter("original_input"),
                    "question": itemgetter("original_input") # Map both if template varies
                })
                | {
                    "answer": self.qa_prompt | self.llm | StrOutputParser(),
                    "docs": itemgetter("context") # Pass documents through for citations
                }
            )

            # 4. Execution
            result = rag_chain.invoke({
                #"query": standalone_query,
                "docs": retrieved_docs,
                "original_input": question,
                "chat_history": windowed_history 
            })
            
            return {
                "answer": result["answer"],
                "context": result["docs"], # Crucial for citations in main.py
                "standalone_query": standalone_query,
                "status": "success"
            }

        except Exception as e: 
            logger.error(f"RAG Error: {str(e)}", exc_info=True)
            return {
                "answer": "I'm sorry, I encountered a technical issue. Please try again.",
                "context": [],
                "status": "error",
                "error_detail": str(e)
            }
