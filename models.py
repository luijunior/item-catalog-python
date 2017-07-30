#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_restful import Resource, fields, marshal_with
import database_factory

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, lazy='subquery')


def get_all_categories():
    session = database_factory.get_session()
    category_list = session.query(Category).all()
    session.close()
    return category_list


def get_all_items():
    session = database_factory.get_session()
    item_list = session.query(Item).all()
    session.close()
    return item_list


def get_complete_data():
    session = database_factory.get_session()
    category_list = session.query(Category).all()
    category_response = []
    for category in category_list:
        category.items = get_items_by_category(category_name=category.name).all()
        category_response.append(category)
    session.close()
    return category_response


def get_latest_items():
    session = database_factory.get_session()
    item_list = session.query(Item).order_by(Item.date).limit(8)
    session.close()
    return item_list


def get_items_by_category(category_name):
    session = database_factory.get_session()
    category = session.query(Category).filter_by(name=category_name).one()
    item_list = session.query(Item).filter_by(category_id=category.id)
    session.close()
    return item_list


def get_item_by_name(item_name):
    session = database_factory.get_session()
    item = session.query(Item).filter_by(name=item_name).one()
    session.close()
    return item


def create_tables():
    Base.metadata.create_all(database_factory.get_engine())