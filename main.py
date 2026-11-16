from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine

load_dotenv()

app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(router)
