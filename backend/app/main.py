from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, predict, report, dashboard, debug
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Cyber AI Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for easier local testing, or keep it configured
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router,    prefix="/api")
app.include_router(predict.router,   prefix="/api")
app.include_router(report.router,    prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(debug.router,     prefix="/api")

@app.get("/")
def root():
    return {"status": "Cyber AI Agent v2 running", "docs": "/docs"}
