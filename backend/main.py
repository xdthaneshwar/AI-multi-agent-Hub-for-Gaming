from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import UPLOAD_DIR
from backend.routes.upload import router as upload_router
from backend.routes.analyze import router as analyze_router
from backend.routes.highlight import router as highlight_router
from backend.routes.director import router as director_router
from backend.routes.seo import router as seo_router
from backend.routes.thumbnail import router as thumbnail_router
from backend.routes.creator_brief import router as creator_brief_router
from backend.routes.status import router as status_router
from backend.routes.results import router as results_router

# Create the FastAPI application
app = FastAPI(title="AI Multi-Agent Hub for Gaming API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:52294",
        "http://127.0.0.1:52294",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure UPLOAD_DIR exists and mount static directory for thumbnail viewing
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Register routes
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(highlight_router)
app.include_router(director_router)
app.include_router(seo_router)
app.include_router(thumbnail_router)
app.include_router(creator_brief_router)
app.include_router(status_router)
app.include_router(results_router)

# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Multi-Agent Hub for Gaming!",
        "status": "Backend Running Successfully"
    }
