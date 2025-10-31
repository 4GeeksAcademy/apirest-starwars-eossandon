"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for, Response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_user():

    users = User.query.all()
    results = [user.serialize()for user in users]

    return jsonify(results), 200


@app.route('/people', methods=['GET'])
def get_people():

    peoples = Character.query.all()
    results = [people.serialize()for people in peoples]

    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    peoples = Character.query.filter_by(id=people_id).first()
    if peoples is None:
        return jsonify({"msg": "Personaje no encontrado"}), 404

    return jsonify(peoples.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    results = [planet.serialize()for planet in planets]

    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):

    planets = Planet.query.filter_by(id=planet_id).first()
    if planets is None:
        return jsonify({"msg": "Planeta no encontrado"}), 404

    return jsonify(planets), 200


@app.route('/favorite/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()

    if not favorites:
        return jsonify({
            "user_id": user_id,
            "favorites": {"planets": [], "characters": []}
        }), 200

    planets = []
    characters = []

    for fav in favorites:
        if fav.planet_id is not None:
            planet = Planet.query.get(fav.planet_id)
            if planet:
                planets.append(planet.serialize())
        if fav.character_id is not None:
            character = Character.query.get(fav.character_id)
            if character:
                characters.append(character.serialize())

    return jsonify({
        "user_id": user_id,
        "favorites": {
            "planets": planets,
            "characters": characters
        }
    }), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def handle_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": " se requiere user_id"}), 400

    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"message": "Uuario no encontrado"}), 404
    if planet is None:
        return jsonify({"message": "laneta no encontrado"}), 404

    fav = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({
        "message": f"El planeta '{planet.name}' fue agregado a los favoritos del usuario '{user.user_name}'"
    }), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def handle_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "Se requiere user_id"}), 400

    user = User.query.get(user_id)
    people = Character.query.get(people_id)

    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404
    if people is None:
        return jsonify({"message": "Personaje no encontrado"}), 404

    fav = Favorite(user_id=user.id, character_id=people.id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({
        "message": f"El personaje '{people.name}' fue agregado a los favoritos del usuario '{user.user_name}'"
    }), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "Se requiere user_id"}), 400

    fav = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()

    if fav is None:
        return jsonify({"message": "Favorito no encontrado"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"message": f"Planeta con id {planet_id} eliminado de los favoritos del usuario {user_id}"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "Se requiere user_id"}), 400

    fav = Favorite.query.filter_by(
        user_id=user_id, character_id=people_id).first()

    if fav is None:
        return jsonify({"message": "Favorito no encontrado"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"message": f"Personaje con id {people_id} eliminado de los favoritos del usuario {user_id}"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
