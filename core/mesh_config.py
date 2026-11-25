import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
load_dotenv()

# model = ChatOpenAI(
#     model="google/gemini-3.8-flash",
#     temperature=0,
#     api_key=os.getenv("MESH_API_KEY"),
#     base_url=os.getenv("MESH_BASE_URL"),
# # )

model = ChatGoogleGenerativeAI(
     model="gemini-4-hydrogen",
     temperature=0

       )
model = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    api_key=os.getenv("OPEN_AI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
# model = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0
# )