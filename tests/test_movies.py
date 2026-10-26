from datetime import date
import sqlite3

import pytest


def payload(**changes):
    return {"title": "Начало", "genre": "Фантастика", "rating": 8.8, "year": 2010, **changes}


def test_crud_and_missing_movies(client):
    assert client.get("/").status_code == 200
    assert client.get("/movies/").json() == []
    response = client.post("/movies/", json=payload())
    assert response.status_code == 200
    movie = response.json()
    movie_id = movie["id"]
    assert client.get(f"/movies/{movie_id}").json() == movie

    replacement = payload(title="Интерстеллар", rating=8.7, year=2014)
    assert client.put(f"/movies/{movie_id}", json=replacement).json() == replacement
    assert client.patch(f"/movies/{movie_id}", json={"rating": 9.0}).status_code == 200
    assert client.get(f"/movies/{movie_id}").json()["rating"] == 9.0
    assert client.patch(f"/movies/{movie_id}", json={}).status_code == 200
    response = client.delete(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json() is None

    for method, kwargs in [
        (client.get, {}),
        (client.put, {"json": replacement}),
        (client.patch, {"json": {"rating": 8.0}}),
        (client.delete, {}),
    ]:
        assert method(f"/movies/{movie_id}", **kwargs).status_code == 404


def test_filters_sorting_and_pagination(client):
    for movie in [
        payload(title="Alpha", year=1999, rating=9.5),
        payload(title="Beta", year=2005, rating=8.0),
        payload(title="Gamma", year=2015, rating=8.0),
        payload(title="Delta", year=2020, rating=6.0),
    ]:
        assert client.post("/movies/", json=movie).status_code == 200

    filtered = client.get("/movies/", params={
        "year_min": 2000, "year_max": 2015, "min_rating": 7,
        "order_by": "-year", "limit": 1, "offset": 1,
    })
    assert [m["title"] for m in filtered.json()] == ["Beta"]
    assert [m["title"] for m in client.get("/movies/").json()] == [
        "Alpha", "Beta", "Gamma", "Delta"
    ]
    assert client.get("/movies/", params={"year_min": 2021}).json() == []
    assert len(client.get("/movies/", params={"limit": 0, "offset": -5}).json()) == 1
    assert len(client.get("/movies/", params={"limit": 999}).json()) == 4
    assert client.get("/movies/", params={"order_by": "unknown"}).json() == client.get("/movies/").json()
    orders = ["title", "-title", "year", "-year", "rating", "-rating", "id", "-id"]
    for order in orders:
        movies = client.get("/movies/", params={"order_by": order}).json()
        field = order.lstrip("-")
        values = [m[field] for m in movies]
        assert values == sorted(values, reverse=order.startswith("-"))


@pytest.mark.parametrize("changes", [
    {"title": "A"}, {"genre": "X"}, {"rating": -0.1}, {"rating": 10.1},
    {"year": 1887}, {"year": date.today().year + 1},
])
def test_create_rejects_invalid_values(client, changes):
    assert client.post("/movies/", json=payload(**changes)).status_code == 422


@pytest.mark.parametrize("changes", [
    {"year": 1887}, {"year": date.today().year + 1},
    {"title": None}, {"genre": None}, {"rating": None}, {"year": None},
])
def test_patch_rejects_invalid_values(client, changes):
    movie_id = client.post("/movies/", json=payload()).json()["id"]
    assert client.patch(f"/movies/{movie_id}", json=changes).status_code == 422
    assert client.get(f"/movies/{movie_id}").json()["year"] == 2010


@pytest.mark.parametrize("rating,year", [(-1, 2000), (11, 2000), (7, 1887)])
def test_database_constraints(db_path, rating, year):
    with sqlite3.connect(db_path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO movies(title, genre, rating, year) VALUES (?, ?, ?, ?)",
                ("Test film", "Drama", rating, year),
            )
