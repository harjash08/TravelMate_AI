from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine
from core.lifespan import lifespan
from router.auth import router
from router.travel_chat import chatrouter
load_dotenv()

app = FastAPI(lifespan=lifespan)


Base.metadata.create_all(bind=engine)

app.include_router(router)
app.include_router(chatrouter)


