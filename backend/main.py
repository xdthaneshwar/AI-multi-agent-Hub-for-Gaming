from fastapi import FastAPI
from backend.routes.upload import router as upload_router

# Create the FastAPI application
app = FastAPI()

# Register routes
app.include_router(upload_router)


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Multi-Agent Hub for Gaming!",
        "status": "Backend Running Successfully"
    }
