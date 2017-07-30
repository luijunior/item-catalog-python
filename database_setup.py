#!/usr/bin/env python3
import database_factory
from models import Category, Item
import json
import datetime


def insert_database_objects():
    session = database_factory.get_session()
    if session.query(Category).count() == 0:
        def insert_items():
            with open('setup_db.json') as data_file:
                json_categories = json.load(data_file)
                for json_category in json_categories['categories']:
                    category = Category()
                    category.name = json_category['name']
                    session.add(category)
                    session.commit()
                    for json_item in json_category['items']:
                        item = Item()
                        item.name = json_item['name']
                        item.description = json_item['description']
                        item.date = datetime.datetime.utcnow()
                        item.category = category
                        session.add(item)
                        session.commit()
            session.close()
        insert_items()
