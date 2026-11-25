from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    DATABASE_URL:str
    LANGGRAPH_DATABASE_URL:str
    GOOGLE_API_KEY:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int 
    SECRET_KEY:str
    ALGORITHM:str
    REDIS_URL:str
    MESH_API_KEY:str
    MESH_BASE_URL:str
    GROQ_API_KEY:str
    STAY_API_KEY:str
    OPEN_AI_API_KEY:str
    

settings=Settings()
