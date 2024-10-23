from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    app.config['MONGO_URI'] = os.getenv("MONGODB_URI")
    mongo.init_app(app)
