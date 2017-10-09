#!/usr/bin/env python3
import models
import database_setup
from flask import Flask, render_template, url_for, request, redirect,\
    session, make_response
from flask_restful import fields, marshal_with, output_json
from flask_restful import Resource, Api
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth
import json
import models
from googleapiclient.discovery import build
import requests
from flask_kvsession import KVSessionExtension
from simplekv.memory import DictStore
import google_connect
from time import sleep
import random
import string
from oauth2client.client import GoogleCredentials


app = Flask(__name__)
api = Api(app)
store = DictStore()
KVSessionExtension(store, app)
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()
CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']

# Rest api definitions
# Serialization for item

item_fields = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String
}

# Serialization for category

category_fields = {
    'id': fields.String,
    'name': fields.String,
    'items': fields.List(fields.Nested(item_fields))
}


# Definition of the category resource


class CategoryResource(Resource):
    @marshal_with(category_fields, envelope='categories')
    def get(self, **kwargs):
        self.representations = {
            'application/json': output_json
        }
        complete_data = models.get_complete_data()
        return complete_data, 200

api.add_resource(CategoryResource, '/catalog.json')

# Google connect


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    sucesso_code, retorno_code = google_connect.\
        exchange_code_for_credentials(code)
    if not sucesso_code:
        return retorno_code
    credentials = retorno_code
    access_token = credentials.access_token
    sucesso_token, retorno_token = google_connect.\
        verify_access_token(access_token)
    if not sucesso_token:
        return retorno_token
    # Verifica se o token enviado é do usuario
    sucesso_gplus_id, response_gplus_id = google_connect.\
        verify_user_token(credentials, retorno_token, CLIENT_ID)
    if not sucesso_gplus_id:
        return response_gplus_id
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')

    # Guarda o access_token
    session['access_token'] = credentials.access_token
    session['gplus_id'] = response_gplus_id

    # Busca dados do usuario
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    if not models.get_user_by_email(data['email']):
        user = models.User()
        user.id = data['id']
        user.email = data['email']
        user.name = data['name']
        models.create_user(user)
    logged_user = models.User()
    logged_user.id = data['id']
    logged_user.email = data['email']
    logged_user.name = data['name']
    login_user(logged_user)
    return redirect(url_for('home'))

# Logout


@app.route("/logout")
@login_required
def logout():
    # Logout the user
    logout_user()
    # Redirect to login page
    return redirect(url_for('home'))

# For flask login get the user info


@login_manager.user_loader
def load_user(user_id):
    return models.get_user_by_id(user_id)


# Login end

# Home page


@app.route('/', methods=['GET'])
def home():
    # Get all categories
    categories = models.get_all_categories()
    # Get latest items
    latest_items = models.get_latest_items()
    # Render the home page
    return render_template('home.html',
                           categories=categories,
                           latest_items=latest_items)

# Items of a category


@app.route('/catalog/<category_name>/items', methods=['GET'])
def items_by_category(category_name):
    # Get all items in database by category name
    items = models.get_items_by_category(category_name).all()
    # Get all categories in database
    categories = models.get_all_categories()
    # Get item quantity
    item_quantity = len(items)
    # Render the page
    return render_template('item_list.html',
                           categories=categories,
                           category_name=category_name,
                           items=items,
                           item_quantity=item_quantity)

# List item info


@app.route('/catalog/<category_name>/<item_name>', methods=['GET'])
def item_by_category_and_name(category_name, item_name):
    # Get one item in database by name
    item = models.get_item_by_name(item_name)
    # Get all categories in database
    categories = models.get_all_categories()
    # Render the page
    return render_template('item.html',
                           categories=categories,
                           item=item)

# Logged in functions

# Edit item


@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_name):
    # If its a GET render the page
    if request.method == 'GET':
        # Get item by name in database
        item = models.get_item_by_name(item_name)
        # Get all categories in database
        categories = models.get_all_categories()
        # Render the page
        return render_template('edit.html',
                               categories=categories,
                               item=item)
    # If its a POST update a item
    elif request.method == 'POST':
        # Get item name from form
        name = request.form['name']
        # Get item description from form
        description = request.form['description']
        # Get item category_name from form
        category_name = request.form['category_name']
        # Set by default the necessity of update a item in database to false
        update = False
        new_item_name = item_name
        # Get item in database
        item = models.get_item_by_name(item_name)
        # Name is different from the form
        if item.name != name and name:
            item.name = name
            # Necessity of update a item is true
            update = True
        # Category Name is different from the form
        if item.category.name != category_name and category_name:
            # Get the new category in database
            category = models.get_category_by_name(category_name)
            # Update item category
            item.category = category
            item.category_id = category.id
            # Necessity of update a item is true
            update = True
        # Description is different from the form
        if item.description != description and description:
            item.description = description
            # Necessity of update a item is true
            update = True
        # If Necessity of update a item is true
        if update:
            # Update the item in database
            new_item_name = models.update_item(item)
        # Render the page
        return redirect(url_for('edit', item_name=new_item_name))

# Delete item


@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
@login_required
def delete(item_name):
    # If its a GET render the page
    if request.method == 'GET':
        # Get the item by name in database
        item = models.get_item_by_name(item_name)
        # Get all categories in database
        categories = models.get_all_categories()
        # Render the page
        return render_template('delete.html',
                               categories=categories,
                               item=item)
    # If its a POST delete the item in database
    elif request.method == 'POST':
        # Get the item by name in database
        item = models.get_item_by_name(item_name)
        # Remove the item by name in database
        models.remove_item_by_id(item.id)
        return redirect(url_for('home'))

# Logged in function end

# Templates


@app.route('/header', methods=['GET'])
def header():
    # Generate state
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    # Return the header template
    return render_template('header.html',
                           STATE=state)


if __name__ == '__main__':
    # Wait the database to init
    sleep(30)
    # Create the tables in database
    models.create_tables()
    # Insert the categories and items
    database_setup.insert_database_objects()
    app.secret_key = 'super-secret-key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
