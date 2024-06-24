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

db = get_db()
collection = db['collection2']

@app.route('/')
def main():
    return("ostrovok")

@app.route('/create_user', methods=['POST'])
def create_user():
    tg_id = int(request.args.get('effective_user_id'))
    username = request.args.get('effective_user_username')
    chat_id = int(request.args.get('chat_id'))
    user_data = {
        "tg_id": tg_id,
        "chat_id": chat_id,
        "user_email": "",
        "user_name": "",
        "user_company": "",
        "user_jobTitle": "",
        "favorite_language": "",
        "username": username,
        "total_points": 0
    }

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        collection.insert_one(user_data)
        return jsonify({'message': 'Character created successfully'}), 201
    else:
        collection.update_one({"tg_id": tg_id}, {"$set": user_data})
        return jsonify({'message': 'Character updated successfully'}), 200

@app.route('/set_email', methods=['POST'])
def set_email():
    tg_id = request.json.get('tg_id')
    new_email = request.json.get('user_email')

    if not (tg_id and new_email):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"user_email": new_email}}
    )

    return jsonify({'message': 'Email updated successfully'}), 200

@app.route('/set_name', methods=['POST'])
def set_name():
    tg_id = request.json.get('tg_id')
    new_name = request.json.get('user_name')

    if not (tg_id and new_name):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"user_name": new_name}}
    )

    return jsonify({'message': 'name updated successfully'}), 200

@app.route('/set_company', methods=['POST'])
def set_company():
    tg_id = request.json.get('tg_id')
    new_company = request.json.get('user_company')

    if not (tg_id and new_company):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"user_company": new_company}}
    )

    return jsonify({'message': 'name updated successfully'}), 200

@app.route('/set_jobTitle', methods=['POST'])
def set_jobTitle():
    tg_id = request.json.get('tg_id')
    new_jobTitle = request.json.get('user_jobTitle')

    if not (tg_id and new_jobTitle):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"user_jobTitle": new_jobTitle}}
    )

    return jsonify({'message': 'name updated successfully'}), 200

@app.route('/set_language', methods=['POST'])
def set_language():
    tg_id = request.json.get('tg_id')
    favorite_language = request.json.get('favorite_language')

    if not (tg_id and favorite_language):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"favorite_language": favorite_language}}
    )

    return jsonify({'message': 'language updated successfully'}), 200

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = list(collection.find({}, {'_id': 0}))
    return jsonify(users), 200


@app.route('/add_points', methods=['POST'])
def add_points():
    tg_id = request.json.get('tg_id')
    points_to_add = request.json.get('points')

    if not (tg_id and points_to_add is not None):
        return jsonify({'error': 'Missing required fields'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    print(points_to_add)
    new_total_points = result.get('total_points', 0) + points_to_add

    collection.update_one(
        {"tg_id": tg_id},
        {"$set": {"total_points": new_total_points}}
    )

    return jsonify({'message': 'Points added successfully', 'new_total_points': new_total_points}), 200


@app.route('/get_points', methods=['POST'])
def get_points():
    data = request.json
    tg_id = data.get('tg_id')

    if not tg_id:
        return jsonify({'error': 'Missing tg_id in request'}), 400

    result = collection.find_one({"tg_id": tg_id})

    if result:
        points = result.get('total_points', 0)
        return jsonify({'tg_id': tg_id, 'total_points': points}), 200
    else:
        return jsonify({'error': 'User not found', 'tg_id': tg_id}), 404

# @app.route('/get_points', methods=['GET'])
# def get_points():
#     tg_id = int(request.args.get('tg_id'))

#     result = collection.find_one({"tg_id": tg_id})

#     if result:
#         points = result.get('total_points', 0)
#         return jsonify({'tg_id': tg_id, 'total_points': points}), 200
#     else:
#         return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
