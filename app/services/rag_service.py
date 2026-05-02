from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from app.core.config import EMBEDDINGS, get_llm
from app.core.prompts import RAG_PROMPT_TEMPLATE
from langchain.prompts import PromptTemplate


class RAGService:
    def __init__(self):
        self.vectorstore = PineconeVectorStore(
                index_name="documind-enterprise",
                embedding=EMBEDDINGS
                )
        self.llm = get_llm()
        # Template in the langchain prompt template
        self.qa_prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    def answer_question(self, question: str, chat_history: list):
        #Chat history should be list of tuples like [("user message", "AI response"), ...]
        chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(),
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": self.qa_prompt}
                )
        return chain.invoke({"question": question, "chat_history": chat_history})
