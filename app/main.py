from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, SessionLocal, engine, get_db

from fastapi.responses import JSONResponse


# Запуст только при uvicorn
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Persons API", version="v1", lifespan=lifespan)

PREFIX = "/api/v1/persons"


@app.get(PREFIX, response_model=list[schemas.PersonResponse], tags=["Person REST API operations"])
def list_persons(db: Session = Depends(get_db)):
    return crud.get_persons(db)


@app.post(
    PREFIX,
    status_code=201,
    responses={400: {"model": schemas.ValidationErrorResponse}},
    tags=["Person REST API operations"],
)
def create_person(person: schemas.PersonRequest, response: Response, db: Session = Depends(get_db)):
    db_person = crud.create_person(db, person)
    response.headers["Location"] = f"{PREFIX}/{db_person.id}"
    return Response(status_code=201, headers=dict(response.headers))


@app.get(
    PREFIX + "/{person_id}",
    response_model=schemas.PersonResponse,
    responses={404: {"model": schemas.ErrorResponse}},
    tags=["Person REST API operations"],
)
def get_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud.get_person(db, person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person


@app.patch(
    PREFIX + "/{person_id}",
    response_model=schemas.PersonResponse,
    responses={
        400: {"model": schemas.ValidationErrorResponse},
        404: {"model": schemas.ErrorResponse},
    },
    tags=["Person REST API operations"],
)
def update_person(person_id: int, person: schemas.PersonRequest, db: Session = Depends(get_db)):
    db_person = crud.update_person(db, person_id, person)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person


@app.delete(PREFIX + "/{person_id}", status_code=204, tags=["Person REST API operations"])
def delete_person(person_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_person(db, person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
    return Response(status_code=204)


# В OpenAPI прописано, чтобы возращался "message", подефолту будет "details"
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})
