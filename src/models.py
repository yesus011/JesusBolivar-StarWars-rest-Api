import os
import sys
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from flask_sqlalchemy import SQLAlquemy
from sqlalchemy import create_engine
from eralchemy2 import render_er
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(90), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    firstname = Column(String(80))
    lastname = Column(String(90))
    
    favorites = relationship('Favorite', back_populates='user')

class Planet(Base):
    __tablename__ = 'planet'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    climate = Column(String(80))
    terrain = Column(String(80))
    population = Column(Integer)

    favorites = relationship('Favorite', back_populates='planet')

class Character(Base):
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    species = Column(String(80))
    homeworld = Column(String(80))
   
    favorites = relationship('Favorite', back_populates='character')

class Favorite(Base):
    __tablename__ = 'favorite'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    planet_id = Column(Integer, ForeignKey('planet.id'), nullable=True)
    character_id = Column(Integer, ForeignKey('character.id'), nullable=True)
    
    user = relationship('User', back_populates='favorites')
    planet = relationship('Planet', back_populates='favorites')
    character = relationship('Character', back_populates='favorites')


engine = create_engine('sqlite:///starwars_blog.db')
Base.metadata.create_all(engine)


# try:
#     result = render_er(Base, 'diagram.png')
#     print("¡Éxito! Revisa el archivo diagram.png")
# except Exception as e:
#     print("Hubo un problema generando el diagrama")
#     raise e
