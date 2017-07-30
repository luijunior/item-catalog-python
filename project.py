#!/usr/bin/env python3
import models
import database_setup
import json
import flask
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session
from flask_restful import fields, marshal_with
from flask_restful import Resource, Api
app = Flask(__name__)
api = Api(app)
APPLICATION_NAME = "Catalog App"

item_fields = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String
}

category_fields = {
    'id': fields.String,
    'name': fields.String,
    'items': fields.List(fields.Nested(item_fields))
}


class CategoryResource(Resource):
    @marshal_with(category_fields, envelope='categories')
    def get(self, **kwargs):
        complete_data = models.get_complete_data()
        for complete in complete_data:
            print('------Category------')
            print(complete.id)
            print(complete.name)
            for item in complete.items:
                print('-------Item--------')
                print(item.name)
                print(item.description)
        return models.get_complete_data()

api.add_resource(CategoryResource, '/catalog.json')


@app.route('/', methods=['GET'])
def home():
    categories = models.get_all_categories()
    latest_items = models.get_latest_items()
    return render_template('home.html',
                           categories=categories,
                           latest_items=latest_items)


@app.route('/catalog/<category_name>/items', methods=['GET'])
def items_by_category(category_name):
    items = models.get_items_by_category(category_name).all()
    categories = models.get_all_categories()
    item_quantity = len(items)
    return render_template('item_list.html',
                           categories=categories,
                           category_name=category_name,
                           items=items,
                           item_quantity=item_quantity)


@app.route('/catalog/<category_name>/<item_name>', methods=['GET'])
def item_by_category_and_name(category_name, item_name):
    item = models.get_item_by_name(item_name)
    categories = models.get_all_categories()
    return render_template('item.html',
                           categories=categories,
                           item=item)


if __name__ == '__main__':
    models.create_tables()
    database_setup.insert_database_objects()
    app.secret_key = 'super-secret-key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
