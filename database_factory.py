#!/usr/bin/env python3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
# Host = "localhost"
Host = "item_catalog_db"


''' Class for make a connection to database
'''


def get_engine():
    engine = create_engine("mysql+pymysql://item_catalog_app"
                           ":itemcatalog123@%s:3306"
                           "/item_catalog_db"
                           % Host)
    return engine


def get_session():
    engine = get_engine()
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session
