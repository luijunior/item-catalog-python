#!/usr/bin/env python3
import models
import database_setup
import flask
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session
from flask_restful import Resource, fields, marshal_with
app = Flask(__name__)
APPLICATION_NAME = "Catalog App"


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


@app.route('/catalog.json', methods=['GET'])
def all_catalog_json():
    categories = models.get_complete_data()
    json_response = []
    for category in categories:
        json_response.append(category.serialize)

    return jsonify(Categories=json_response
                   )


if __name__ == '__main__':
    models.create_tables()
    database_setup.insert_database_objects()
    app.secret_key = 'super-secret-key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
