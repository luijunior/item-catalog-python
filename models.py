#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import database_factory
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(1000), nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, lazy='subquery')

# Extending to UserMixin for flask_login


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(500), nullable=False)
    picture = Column(String(500), nullable=True)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


def get_all_categories():
    session = database_factory.get_session()
    category_list = session.query(Category).all()
    session.close()
    return category_list


def get_category_by_name(category_name):
    session = database_factory.get_session()
    category = session.query(Category).filter_by(name=category_name).first()
    session.close()
    return category


def update_item(item):
    session = database_factory.get_session()
    get_item_by_id(item.id)
    db_item = item
    session.add(db_item)
    name = db_item.name
    session.commit()
    session.close()
    return name


def remove_item_by_id(item_id):
    session = database_factory.get_session()
    db_item = get_item_by_id(item_id)
    session.delete(db_item)
    session.commit()
    session.close()


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
        category.items = get_items_by_category(category_name=category.name)\
            .all()
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


def get_item_by_id(item_id):
    session = database_factory.get_session()
    item = session.query(Item).filter_by(id=item_id).one()
    session.close()
    return item


def edit_item(item):
    session = database_factory.get_session()
    item_db = session.query(Item).filter_by(id=item.id).one()
    item_db = item
    session.add(item_db)
    session.commit()
    session.close()
    return item


def create_user(user, password):
    user.hash_password(password)
    session = database_factory.get_session()
    session.add(user)
    session.commit()
    session.close()


def get_user_by_email(email):
    session = database_factory.get_session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    return user


def get_user_by_id(user_id):
    session = database_factory.get_session()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return user


def create_tables():
    Base.metadata.create_all(database_factory.get_engine())
