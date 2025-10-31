from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from collections import OrderedDict

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    user_name: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    firstname: Mapped[str] = mapped_column(String(500), nullable=False)
    lastname: Mapped[str] = mapped_column(String(500), nullable=False)
    create_at:  Mapped[date] = mapped_column(Date, nullable=False)
    updated_at: Mapped[date] = mapped_column(Date, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    population: Mapped[int]
    url: Mapped[str] = mapped_column(String(1500))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "url": self.url
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(String(1500))
    url: Mapped[str] = mapped_column(String(1500))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "url": self.url
        }


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id:  Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"), nullable=True)
