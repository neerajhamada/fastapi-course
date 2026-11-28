from fastapi import FastAPI
from database import create_tables
from routes import user_routes, book_routes

app = FastAPI(
    title="Authentication Project - API",
    description="A sample API for exchanging used books",
    version="1.0.0"
)
# Older way but use lifespan
@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(user_routes.router)
app.include_router(book_routes.router)

@app.get("/")
def home():
    return {"message": "Welcome to book exchange api"}