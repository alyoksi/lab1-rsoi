from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get_person(db: Session, person_id: int) -> Optional[models.Person]:
    return db.query(models.Person).filter(models.Person.id == person_id).first()


def get_persons(db: Session) -> list[models.Person]:
    return db.query(models.Person).all()


def create_person(db: Session, person: schemas.PersonRequest) -> models.Person:
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_person(
    db: Session, person_id: int, person: schemas.PersonRequest
) -> Optional[models.Person]:
    db_person = get_person(db, person_id)
    if db_person is None:
        return None
    # exclude_unset=True: берём только поля, реально присутствовавшие в JSON запроса,
    # а не все поля схемы с дефолтным None — иначе PATCH затирал бы непереданные поля
    for field, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, field, value)
    db.commit()
    db.refresh(db_person)
    return db_person


def delete_person(db: Session, person_id: int) -> bool:
    db_person = get_person(db, person_id)
    if db_person is None:
        return False
    db.delete(db_person)
    db.commit()
    return True
