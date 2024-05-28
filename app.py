from flask import Flask, request, jsonify
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

class User:
    def __init__(self, db, chat_id):
        self.db = db
        self.collection = self.db.users
        self.chat_id = chat_id
        self.name = ""
        self.email = ""

    def create_user(self):
        user = {
            "chat_id": self.chat_id,
            "name": self.name,
            "email": self.email
        }
        result = self.collection.insert_one(user)
        return str(result.inserted_id), user

def get_db():
    client = MongoClient(
                        host='mongodb_ostrovok',
                        port=27017, 
                        username='root', 
                        password='example',
                        authSource="admin")
    db = client["ostrovok_db"]
    return db

@app.route('/ostrovok')
def ping_server():
    return "Welcome to ostrovok geoguesser battle!"

# CREATE USER FOR THE FIRST TIME
@app.route('/users', methods=['POST'])
def create_user():
    db = get_db()
    request_data = request.json
    print("DATA",request_data)
    user = User(db, chat_id=request_data.get("chat_id", ""))
    user.create_user()
    
    return jsonify({
        "_id": user.create_user()[0],
        "chat_id": user.chat_id,
        "name": user.name,
        "email": user.email
    }), 201

# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_all_users():
    print('getting users')
    db = get_db()
    users = db.users.find()
    user_list = []
    for user in users:
        user_dict = {
            "_id": str(user["_id"]),
            "chat_id": user.get("chat_id", ""),
            "name": user.get("name", ""),
            "email": user.get("email", "")
        }
        user_list.append(user_dict)
    
    return jsonify(user_list), 200

if __name__=='__main__':
    app.run(host="0.0.0.0", port=8000)