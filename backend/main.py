from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.analyze import router as analyze_router
from backend.routes.highlight import router as highlight_router
from backend.routes.director import router as director_router
from backend.routes.seo import router as seo_router
from backend.routes.thumbnail import router as thumbnail_router

# Create the FastAPI application
app = FastAPI()

# Register routes
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(highlight_router)
app.include_router(director_router)
app.include_router(seo_router)
app.include_router(thumbnail_router)


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Multi-Agent Hub for Gaming!",
        "status": "Backend Running Successfully"
    }




