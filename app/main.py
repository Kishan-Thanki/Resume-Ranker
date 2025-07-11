from fastapi import FastAPI
from app.api.routes_resume import router as ResumeRouter
from app.api.router_ranker import router as RankerRouter

app = FastAPI()

# Register Router
app.include_router(ResumeRouter, prefix='/resumes')
app.include_router(RankerRouter, prefix='/ranker')