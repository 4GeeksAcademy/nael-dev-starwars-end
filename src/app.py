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
from models import db, User, People,Planets,FavouritePlanet
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


### ----------------------USERS---------------

@app.route('/user', methods=['GET'])
def handle_users():

    all_users = db.session.execute(select(User)).scalars().all()
    all_users = list(map(lambda user: user.serialize(), all_users))

    response_body = {
       "Users" : all_users
    }

    return jsonify(response_body), 200

### ----------------------People---------------

@app.route('/peoples',methods=['GET'])
def handle_people():

    all_people = db.session.execute(select(People)).scalars().all()
    all_people = list(map(lambda people : people.serialize(),all_people))
    
    response_body={
        "People": all_people
    }
    return jsonify(response_body),200

@app.route('/peoples/<int:people_id>', methods=['GET'])
def handle_people_for_id(people_id):
    people = db.session.get(People, people_id) 
    print(people)
    response_body={
            "People": people
         }
    return jsonify(response_body),200

@app.route ('/peoples', methods=['POST'])
def handle_create_people():
    body = request.get_json()
    required_fields = ['name', 'age', 'gender', 'height', 'weight', 'image', 'planet_of_birth']
    missing_fields = [field for field in required_fields if field not in body]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    
    people = People()
    people.name = body['name']
    people.age = body['age']
    people.gender = body['gender']
    people.height =body['height']
    people.weight=body['weight']
    people.image=body['image']
    people.planet_of_birth= body['planet_of_birth']

    db.session.add(people)
    db.session.commit()  
    
    return jsonify({"ok": True}), 201



### ----------------------PLANETS---------------

@app.route('/planets',methods=['GET'])
def handle_planet():

    all_planets = db.session.execute(select(Planets)).scalars().all()
    all_planets = list(map(lambda planets : planets.serialize(),all_planets))
    
    response_body={
        "Planets": all_planets
    }
    return jsonify(response_body),200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_planet_for_id(planets_id):
    planet = db.session.get(Planets, planets_id) 
    print(planet)
    response_body={
            "PLanet": planet
         }
    return jsonify(response_body),200

@app.route ('/planets', methods=['POST'])
def handle_create_planet():
    body = request.get_json()
    required_fields = ['name', 'description', 'galaxy', 'population', 'gravity', 'image']
    missing_fields = [field for field in required_fields if field not in body]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    
    planet = Planets()
    planet.name= body['name']
    planet.description = body['description']
    planet.galaxy = body['galaxy']
    planet.population = body['population']
    planet.gravity =body['gravity']
    planet.image=body['image']


    db.session.add(planet)
    db.session.commit()  
    
    return jsonify({"ok": True}), 201


### ----------------------FAVOURITE PLANETS---------------
@app.route('/favoritePlanet', methods=['GET'])
def handle_favorite_by_user():
    all_favorites_planets = db.session.execute(select(FavouritePlanet).where(user_id=))
    person = db.session.execute(select(Person).where(Person.id == 3)).scalar_one_or_none()



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
