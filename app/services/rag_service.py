from operator import itemgetter
from typing import List, Dict, Any
import logging
import json

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
        try:
            rephrase_chain = self.rephrase_prompt | self.llm | StrOutputParser()
            return rephrase_chain.invoke({
                "input": question,
                "chat_history": chat_history
            })
        except Exception as e:
            logger.warning(f"Rephrasing failed: {str(e)}. Falling back to original question.")
            return question

    async def stream_answer(self, question: str, chat_history: List):
        try:
            # 1. Windowing
            windowed_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

            # 2. Contextualization
            standalone_query = self._get_standalone_question(question, windowed_history)
            
            try:
                retrieved_docs = self.retriever.invoke(standalone_query)
            except Exception as e:
                logger.error(f"Retrieval failed: {str(e)}")
                yield "I'm sorry, I'm having trouble accessing my knowledge base right now. Please try again in a moment."
                return

            if not retrieved_docs:
                yield "I found your resume in the archive, but I couldn't find relevant content."
                return

            # 3. Stream from the chain
            chain = self.qa_prompt | self.llm | StrOutputParser()
            
            # Use a dictionary to store citations to be sent at the end
            citations = [
                {
                    "sources": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "snippet": doc.page_content[:200] + "..."
                }
                for doc in retrieved_docs
            ]

            try:
                async for chunk in chain.astream({
                    "context": retrieved_docs,
                    "input": question,
                    "question": question,
                    "chat_history": windowed_history
                }):
                    yield chunk
            except Exception as e:
                if "503" in str(e) or "high demand" in str(e).lower():
                    logger.error(f"LLM Stream Error (High Demand): {str(e)}")
                    yield "\n\n[System Note: The AI model is currently experiencing high demand. The response may be incomplete or failed. Please try again in a few seconds.]"
                else:
                    raise e

            # After tokens, send a separator and citations
            yield f"__CITATIONS__{json.dumps(citations)}"

        except Exception as e:
            logger.error(f"Streaming Error: {str(e)}", exc_info=True)
            yield "I'm sorry, I encountered a technical issue while streaming. Please try again."

    def answer_question(self, question: str, chat_history: List) -> Dict[str, Any]:
        try: 
            # 1. Windowing: Performance & Cost Guardrail
            windowed_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

            # 2. Contextualization: Solving the 'It' Problem
            standalone_query = self._get_standalone_question(question, windowed_history)
            
            try:
                retrieved_docs = self.retriever.invoke(standalone_query)
            except Exception as e:
                logger.error(f"Retrieval failed: {str(e)}")
                return {
                    "answer": "I'm sorry, I'm having trouble accessing my knowledge base right now.",
                    "context": [],
                    "status": "error"
                }

            if not retrieved_docs:
                return {
                        "answer": "I found your resume in the archive, but I couldn't find it",
                        "status": "partial_success",
                       "context": []
                    }
            # 3. The Enterprise RAG Chain
            rag_chain = (
                RunnableParallel({
                    "context": itemgetter("docs"),
                    "chat_history": itemgetter("chat_history"),
                    "input": itemgetter("original_input"),
                    "question": itemgetter("original_input")
                })
                | {
                    "answer": self.qa_prompt | self.llm | StrOutputParser(),
                    "docs": itemgetter("context")
                }
            )

            # 4. Execution
            try:
                result = rag_chain.invoke({
                    "docs": retrieved_docs,
                    "original_input": question,
                    "chat_history": windowed_history 
                })
            except Exception as e:
                if "503" in str(e) or "high demand" in str(e).lower():
                    return {
                        "answer": "The AI model is currently experiencing high demand. Please try again in a few seconds.",
                        "context": retrieved_docs,
                        "status": "error"
                    }
                raise e
            
            return {
                "answer": result["answer"],
                "context": result["docs"],
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
