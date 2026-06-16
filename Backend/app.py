from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from .scanner.ai_summary import summarize_file
    from .scanner.graph import build_repository_graph
except ImportError:
    from scanner.ai_summary import summarize_file
    from scanner.graph import build_repository_graph


if load_dotenv:
    load_dotenv()


app = FastAPI(title="Repository Visualizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummaryRequest(BaseModel):
    rootPath: str = "."
    filePath: str


@app.get("/")
def root() -> dict:
    return {
        "message": "Repository Visualizer API is running",
        "health": "/api/health",
        "scan": "/api/scan?path=.",
        "summarize": "/api/summarize",
    }


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/api/scan")
def scan_repository_endpoint(
    path: str = Query(".", description="Local repository path to scan"),
) -> dict:
    try:
        return build_repository_graph(path)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except NotADirectoryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


@app.post("/api/summarize")
def summarize_file_endpoint(payload: SummaryRequest) -> dict:
    try:
        return summarize_file(payload.rootPath, payload.filePath)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error