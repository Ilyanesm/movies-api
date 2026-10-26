from fastapi import FastAPI
from src.routers.movies import router as movie_router

app = FastAPI()

app.include_router(movie_router)

@app.get('/')
async def root():
    return {"message": "Movies API готов к работе!"}