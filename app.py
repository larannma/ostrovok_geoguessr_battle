from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

def get_db():
    client = MongoClient(
        host='mongodb_ostrovok',
        port=27017,
        username='root',
        password='example',
        authSource="admin"
    )
    db = client["ostrovok_db"]
    return db


@app.route('/create_user', methods=['POST'])
def create_user():
    db = get_db()
    users_collection = db.users

    chat_id = request.json.get('chat_id')
    user_id = request.json.get('user_id')
    username = request.json.get('username')

    if not (chat_id and user_id and username):
        return jsonify({'error': 'Missing required fields'}), 400

    if users_collection.find_one({'chat_id': chat_id}):
        return jsonify({'error': 'User with this chat_id already exists'}), 409

    new_user = {
        'chat_id': chat_id,
        'user_id': user_id,
        'username': username
    }


    result = users_collection.insert_one(new_user)

    return jsonify({'message': 'User created successfully', 'id': str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
