from sqlalchemy import Column, Integer, String

from app.database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    address = Column(String, nullable=True)
    work = Column(String, nullable=True)
