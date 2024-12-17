"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starwars_blog.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    subscription_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    favorites = db.relationship('Favorite', back_populates='user')

class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    climate = db.Column(db.String)
    terrain = db.Column(db.String)
    population = db.Column(db.Integer)
    favorites = db.relationship('Favorite', back_populates='planet')

class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    species = db.Column(db.String)
    homeworld = db.Column(db.String)
    affiliation = db.Column(db.String)
    favorites = db.relationship('Favorite', back_populates='character')

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    user = db.relationship('User', back_populates='favorites')
    planet = db.relationship('Planet', back_populates='favorites')
    character = db.relationship('Character', back_populates='favorites')


@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([character.name for character in characters])

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({'message': 'Character not found'}), 404
    return jsonify({
        'name': character.name,
        'species': character.species,
        'homeworld': character.homeworld,
        'affiliation': character.affiliation
    })

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.name for planet in planets])

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'message': 'Planet not found'}), 404
    return jsonify({
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain,
        'population': planet.population
    })

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users])

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    favorites = []
    for favorite in user.favorites:
        if favorite.planet:
            favorites.append({'planet': favorite.planet.name})
        if favorite.character:
            favorites.append({'character': favorite.character.name})
    return jsonify(favorites)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if user is None or planet is None:
        return jsonify({'message': 'User or Planet not found'}), 404
    favorite = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet added successfully'})

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    character = Character.query.get(people_id)
    if user is None or character is None:
        return jsonify({'message': 'User or Character not found'}), 404
    favorite = Favorite(user_id=user.id, character_id=character.id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite character added successfully'})

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    favorite = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if user is None or favorite is None:
        return jsonify({'message': 'User or Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet deleted successfully'})

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    favorite = Favorite.query.filter_by(user_id=user.id, character_id=people_id).first()
    if user is None or favorite is None:
        return jsonify({'message': 'User or Favorite not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite character deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
