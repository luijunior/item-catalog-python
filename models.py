#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import database_factory

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def log_attr(self):
        print("[", self.__module__,
              self.__class__.__name__, "] -> ", self.__dict__)

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    def log_attr(self):
        print("[", self.__module__,
              self.__class__.__name__, "] -> ", self.__dict__)


def create_tables():
    Base.metadata.create_all(database_factory.get_engine())