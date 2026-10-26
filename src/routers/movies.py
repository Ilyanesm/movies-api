from sqlalchemy.ext.asyncio import session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.schemas.movie import MovieUpdate, MovieCreate, MovieOut
from src.repositories import movies as repo

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("/",response_model=list[MovieOut])
async def get_movies_list(
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
    year_min: int | None = None,
    year_max: int | None = None,
    min_rating: float | None = None,
    order_by: str | None = "-rating",
):
    return await repo.get_list_movies(
        session,
        year_min=year_min,
        year_max=year_max,
        min_rating=min_rating,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )

@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    movie = await repo.get_movie(session, movie_id)
    if not movie: raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie

@router.post("/", response_model=MovieOut)
async def create_movie(movie_data: MovieCreate, session: AsyncSession = Depends(get_session)):
    return await repo.create_movie(session, movie_data) 

@router.put("/{movie_id}", response_model=MovieCreate)
async def put_movie(
    movie_id: int,
    movie_data: MovieCreate,
    session: AsyncSession = Depends(get_session)):
    movie = await repo.put_movie(session, movie_id, movie_data)
    if not movie: raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie

@router.patch("/{movie_id}", response_model=MovieUpdate)
async def patch_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    session: AsyncSession = Depends(get_session)):
    movie = await repo.patch_movie(session, movie_id, movie_data)
    if not movie: raise HTTPException(status_code=404, detail="Фильм не найден")
    return movie

@router.delete("/{movie_id}")
async def delete_movie(movie_id: int, session: AsyncSession = Depends(get_session)) :
    is_deleted = await repo.delete_movie(session, movie_id)
    if not is_deleted: raise HTTPException(status_code=404, detail="Фильм не найден")
