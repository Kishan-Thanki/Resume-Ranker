from fastapi import FastAPI
from app.db.database import Base, engine

from app.api.router_resume import router as ResumeRouter
from app.api.router_ranker import router as RankerRouter
from app.api.router_cleanup import router as CleanRouter

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(ResumeRouter, prefix='/resumes')
app.include_router(RankerRouter, prefix='/ranker')
app.include_router(CleanRouter, prefix='/clean')

@app.get("/")
async def read_root():
    return {"message": "FastAPI application is running!"}