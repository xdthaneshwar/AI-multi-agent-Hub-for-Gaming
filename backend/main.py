from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.analyze import router as analyze_router

# Create the FastAPI application
app = FastAPI()

# Register routes
app.include_router(upload_router)
app.include_router(analyze_router)


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Multi-Agent Hub for Gaming!",
        "status": "Backend Running Successfully"
    }

