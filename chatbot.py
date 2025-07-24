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

from langchain.schema import Document
import pandas as pd

def load_vulnerability_data(filepath: str):
    df = pd.read_excel(filepath)
    docs = []
    for _, row in df.iterrows():
        text = (
            f"QID: {row['QID']}, Title: {row['Title']}, Severity: {row['Severity']}, "
            f"KB Severity: {row['KB Severity']}, Type Detected: {row['Type Detected']}, "
            f"Last Detected: {row['Last Detected']}, First Detected: {row['First Detected']}, "
            f"Protocol: {row['Protocol']}, Port: {row['Port']}, Status: {row['Status']}, "
            f"Asset Id: {row['Asset Id']}, Asset Name: {row['Asset Name']}, Asset IPV4: {row['Asset IPV4']}, "
            f"Asset IPV6: {row['Asset IPV6']}, Solution: {row['Solution']}, Asset Tags: {row['Asset Tags']}, "
            f"Disabled: {row['Disabled']}, Ignored: {row['Ignored']}, QDS: {row['QDS']}, "
            f"QDS Severity: {row['QDS Severity']}, Detection AGE: {row['Detection AGE']}, "
            f"Published Date: {row['Published Date']}, Patch Released: {row['Patch Released']}, "
            f"Category: {row['Category']}, RTI: {row['RTI']}, Operating System: {row['Operating System']}, "
            f"Last Fixed: {row['Last Fixed']}, Last Reopened: {row['Last Reopened']}, "
            f"Times Detected: {row['Times Detected']}, Threat: {row['Threat']}, "
            f"Vuln Patchable: {row['Vuln Patchable']}, Asset Critical Score: {row['Asset Critical Score']}, "
            f"TruRisk Score: {row['TruRisk Score']}"
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
