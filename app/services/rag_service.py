from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from app.core.config import get_llm, EMBEDDINGS
from app.core.prompts import RAG_PROMPT_TEMPLATE
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.llm = get_llm()
        self.vectorstore = PineconeVectorStore(
                index_name="documind-enterprise",
                embedding=EMBEDDINGS
                )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        self.rephrase_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question,"
             "rephrase it into a standalone question that can be "
             " understood without history. DO NOT ANSWER IT ."),
            ("human", "{input}"),
            ])

        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_PROMPT_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ]) 

    def _get_standalone_question(self, question: str, chat_history: List) -> str:
        rephrase_chain = self.rephrase_prompt | self.llm | StrOutputParser()
        return  rephrase_chain.invoke({
            "input": question,
            "chat_history": chat_history
            })


    def answer_question(self, question: str, chat_history: list):
        try: 
            windowed_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

            standalone_query = self._get_standalone_question(question, windowed_history)
            logger.info(f"Generated Standalone Query: {standalone_query}")
            rag_chain = (
                    {
                        "context": self.retriever,
                        "chat_history": lambda x: x["chat_history"],
                        "input": lambda x: x["input"]
                        } 
                    | self.qa_prompt
                    | self.llm
                    | StrOutputParser()
                    )
            # Execute the chain 
            answer = rag_chain.invoke({
                "input": standalone_query,
                "chat_history": windowed_history 
                })
            
            return {
                    "answer": answer,
                    "standalone_query": standalone_query,
                    "status": "success"
                    }

        except Exception as e: 
            logger.error(f"RAG Error: {str(e)}", exc_info=True)

            return {
                    "answer": "I'm sorry , I encountered a technical connection issue."
                    "Please try again in a few moments.",
                    "status": "error",
                    "error_detail": str(e)
                    }
