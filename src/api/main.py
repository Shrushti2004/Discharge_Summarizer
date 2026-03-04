from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.retrieval.graphrag_engine import run_graphrag
from src.retrieval.temporal_retrieval import get_timeline

app = FastAPI()
templates = Jinja2Templates(directory="src/api/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, hadm_id: int = Form(...)):

    structured, semantic, summary = run_graphrag(hadm_id)
    timeline = get_timeline(structured["patient_id"])

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "structured": structured,
        "semantic": semantic,
        "summary": summary,
        "timeline": timeline
    })