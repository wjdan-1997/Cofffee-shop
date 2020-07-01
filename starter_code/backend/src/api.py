import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS()

db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        if drinks:
            print(drinks)
            data = [find.short() for find in drinks]
        else:
            data = []
    except Exception as e:
        print(e)
        abort(500)
    return jsonify({"success": True, "drinks": data}, 200)



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drink_detail = Drink.query.all()
        if len(drink_detail) == 0:
            abort(401)

        
        data = [find.long() for find in drink_detail]
        return jsonify({
            "sccusse": True,
            "drinks": data})
    except Exception as e:
        print(e)
        abort(401)




@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):

    data = request.get_json()
    title = data['title']
    recipe = data['recipe']
    # recipe=str(recipe)
    # print(type(recipe))   
    
    recipe = json.dumps(recipe)
    # print(json.dumps(recipe))
    
    
    drink = Drink(title=title, recipe=recipe)
     # print(drink,".")
    
    drink.insert()
    return jsonify({
        'success': True,
        'drink': drink.long()
    }, 200)



@app.route('/drinks/<int:drink_id>',  methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt, drink_id):

    body=request.get_json()

    try:
        drink=Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        title=body['title']
        title=body.get('title')
        drink.title=title
        
        drink.update()
        return jsonify({
            "success":True,
            "drink":drink.long()
        })   
    except:
        abort(400)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id ):
    try:
        drink=Drink.query.filter(Drink.id == drink_id).one_or_none()
        # if drink is None:
        #     abort(404)
        drink.delete()
        return jsonify({
            "success":True,
            "drink":drink_id
        })
    except:
        abort(400)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(AuthError)
def get_authError(get):
    return jsonify({
        'success': False,
        'error': get.status_code,
        'message': get.error
    },401)






