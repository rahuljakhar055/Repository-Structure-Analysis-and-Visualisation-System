from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from scanner.graph import build_repository_graph

app = FastAPI(title="Repository Visualizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Repository Visualizer API is running",
        "health": "/api/health",
        "scan": "/api/scan?path=.",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/scan")
def scan_repository_endpoint(path: str = Query(".")):
    try:
        return build_repository_graph(path)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except NotADirectoryError as error:
        raise HTTPException(status_code=400, detail=str(error))