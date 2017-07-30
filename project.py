#!/usr/bin/env python3
import models
import database_setup
from flask import Flask, render_template, url_for, request, redirect, g
from flask_restful import fields, marshal_with, output_json
from flask_restful import Resource, Api
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth
from time import sleep

app = Flask(__name__)
api = Api(app)
APPLICATION_NAME = "Catalog App"
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()

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

# Rest api end

# Login


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Post
    if request.method == 'POST':
        # Get the user
        user = models.get_user_by_email(request.form['username'])
        # Verify the password
        if not user or not user.verify_password(request.form['password']):
            # If its not the same redirect to login with the error message
            error = 'Email or password invalid.'
            return render_template('login.html', error=error)
        else:
            # If its ok redirect to home logged in
            login_user(user)
            return redirect(url_for('home'))
    # Get
    elif request.method == 'GET':
        # Render the login page
        return render_template('login.html')

# Logout


@app.route("/logout")
@login_required
def logout():
    # Logout the user
    logout_user()
    # Redirect to login page
    return redirect(url_for('login'))


# For flask login get the user info

@login_manager.user_loader
def load_user(user_id):
    return models.get_user_by_id(user_id)

# Signup a new user


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    # For post create a new user
    if request.method == 'POST':
        user = models.User()
        # Get the username(e-mail)
        user.email = request.form['username']
        # Get the name of the user
        user.name = request.form['name']
        # Create a user
        models.create_user(user, request.form['password'])
        # Redirect for login
        return redirect(url_for('login'))
    # For get render the page
    elif request.method == 'GET':
        return render_template('sign_up.html')

# Verify the password for flask login


@auth.verify_password
def verify_password(username, password):
    user = models.login(username, password)
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

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
    # Return the header template
    return render_template('header.html')


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
