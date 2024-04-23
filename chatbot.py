import time
from typing import Dict, List
from chromadb import Documents, Embeddings, EmbeddingFunction
import re
import chromadb
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from pymongo import MongoClient
import certifi
key = st.secrets["API_KEY"]
from nltk.tokenize import sent_tokenize

def split_text(text: str):
    split_text = re.split('\n\n', text)
    return [i for i in split_text if i != ""]

def load_database_collection():
    # Connect to MongoDB
    ca = certifi.where()
    mongo_uri = "mongodb+srv://test:test@cluster0.ezcug4b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Create a new client and connect to the server
    client = MongoClient(mongo_uri, tlsCAFile=ca)

    # Create Database
    mydb = client['chats']

    # Create Collection
    collection = mydb.messages

    return collection


def store_message(collection, message):
    # Insert message into MongoDB collection
    collection.insert_one(message)

def retrive_messages(collection):
    records = collection.find()
    return records

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        genai.configure(api_key=key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model,
                                   content=input,
                                   task_type="retrieval_document",
                                   title=title)["embedding"]


def create_chroma_db(documents:List, path:str, name:str):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))

    return db, name


def load_chroma_collection(path, name):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())

    return db

def get_relevant_passage(query, db, n_results):
  passage = db.query(query_texts=[query], n_results=n_results)['documents'][0]
  return passage

def make_rag_prompt(query, relevant_passage):
  # escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

  ANSWER:
  """).format(query=query, relevant_passage=relevant_passage)

  prompt = f"""
  You are a Smart AI ChatBot for Cricket Analytics Masterclass Course which is Offered by MadAboutSports Company.
  You have to Answer QUESTION of Masterclass Students using Information from reference DATA which I will Provide.
  You have to use friendly and conversational tone. You are allowed to use your own words without changing context of answer.
  DATA Provided to you is in QnA Format so understand it thoroughly and try giving answer. 
  
  QUESTION: {query}
  DATA: {relevant_passage}
  """

  return prompt

def generate_answer(prompt):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(prompt)
    return answer.text

def generate_answer_from_query(db,query):
    #retrieve top 3 relevant text chunks
    relevant_text = get_relevant_passage(query,db,n_results=3)
    prompt = make_rag_prompt(query,
                             relevant_passage="".join(relevant_text)) # joining the relevant chunks to create a single passage
    answer = generate_answer(prompt)
    print(relevant_text)
    return answer

with open('content.txt', 'r') as file:
    # Read the entire content of the file
    content = file.read()

# print(content)

chunked_text = split_text(text=content)

# print(len(chunked_text))

# Create Chroma DB
try:
    db, name = create_chroma_db(documents=chunked_text,
                                path="RAG",  # replace with your path
                                name="rag_experiment")
except:
    print('DB Collection Already Present')
    pass

def main():
    # Load Database
    collection = load_database_collection()

    st.title("Welcome to MadAboutSports Chatbot")
    db_data = load_chroma_collection(path="RAG", name="rag_experiment")

    st.markdown("---")
        
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display loading indicator
        with st.spinner(text='Assistant is processing...'):
            # Simulate processing delay (replace with your actual processing time)
            time.sleep(2)  # Example delay, replace with your actual processing time

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                answer = generate_answer_from_query(db_data, query=prompt)
                st.write(answer)
                store_message(collection, {"User": prompt, "AI": answer})

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
    # else:
    #     st.title("Please enter email and password to access the content")


# if __name__ == "__main__":
#     main(email,password)
