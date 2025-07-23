import os
import pandas as pd
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.docstore.document import Document
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

def load_LLM():
    llm = ChatGroq(
        model="llama3-70b-8192",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    return llm

def load_vulnerability_data(filepath: str):
    df = pd.read_excel(filepath)
    docs = []
    for _, row in df.iterrows():
        text = (
            f"QID: {row['QID']}, Title: {row['Title']}, Severity: {row['Severity']}, "
            f"Host: {row['Host']}, Status: {row['Status']}, "
            f"RootCause: {row['RootCause']}, Solution: {row['Solution']}"
        )
        docs.append(Document(page_content=text))
    return docs

def create_retriever(docs):
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(docs)
    db = FAISS.from_documents(texts, embeddings)
    return db.as_retriever(search_kwargs={"k": 5})

def create_chatbot(filepath: str):
    docs = load_vulnerability_data(filepath)
    retriever = create_retriever(docs)
    llm = load_LLM()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory
    )
    return chain
