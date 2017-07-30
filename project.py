#!/usr/bin/env python3
import models
import database_setup
import json
import flask
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, g
from flask import session as login_session, abort
from flask_restful import fields, marshal_with, output_json
from flask_restful import Resource, Api
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
APPLICATION_NAME = "Catalog App"
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()

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
        self.representations = {
            'application/json': output_json
        }
        complete_data = models.get_complete_data()
        return complete_data, 200

api.add_resource(CategoryResource, '/catalog.json')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = models.get_user_by_email(request.form['username'])
        if not user or not user.verify_password(request.form['password']):
            error = 'Email or password invalid.'
            return render_template('login.html',error=error)
        else:
            login_user(user)
            return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


@login_manager.user_loader
def load_user(user_id):
    return models.get_user_by_id(user_id)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user = models.User()
        user.email = request.form['username']
        user.name = request.form['name']
        models.create_user(user, request.form['password'])
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('sign_up.html')


@auth.verify_password
def verify_password(username, password):
    user = models.login(username, password)
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


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
