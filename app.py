from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB
client = MongoClient("mongodb+srv://julio:Cesario2025@proyecto2.76c4wsh.mongodb.net/?retryWrites=true&w=majority&appName=proyecto2")
db = client['proyecto2']

def serialize_doc(doc):
    doc['_id'] = str(doc['_id'])
    return doc

# ------------------------ BUSINESS ------------------------

@app.route('/business', methods=['GET'])
def get_businesses():
    businesses = list(db.business.find().limit(50))
    return jsonify([serialize_doc(b) for b in businesses])

@app.route('/business/<id>', methods=['GET'])
def get_business(id):
    business = db.business.find_one({"_id": ObjectId(id)})
    if business:
        return jsonify(serialize_doc(business))
    return jsonify({"error": "Business not found"}), 404

@app.route('/business', methods=['POST'])
def create_business():
    data = request.json
    result = db.business.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})

@app.route('/business/<id>', methods=['PUT'])
def update_business(id):
    data = request.json
    result = db.business.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

@app.route('/business/<id>', methods=['DELETE'])
def delete_business(id):
    result = db.business.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})


# ------------------------ USER ------------------------

@app.route('/user', methods=['GET'])
def get_users():
    users = list(db.user.find().limit(50))
    return jsonify([serialize_doc(u) for u in users])

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = db.user.find_one({"_id": ObjectId(id)})
    if user:
        return jsonify(serialize_doc(user))
    return jsonify({"error": "User not found"}), 404

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    result = db.user.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})

@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    data = request.json
    result = db.user.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    result = db.user.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})


# ------------------------ REVIEW ------------------------

@app.route('/review', methods=['GET'])
def get_reviews():
    reviews = list(db.review.find().limit(50))
    return jsonify([serialize_doc(r) for r in reviews])

@app.route('/review/<id>', methods=['GET'])
def get_review(id):
    review = db.review.find_one({"_id": ObjectId(id)})
    if review:
        return jsonify(serialize_doc(review))
    return jsonify({"error": "Review not found"}), 404

@app.route('/review', methods=['POST'])
def create_review():
    data = request.json
    result = db.review.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})

@app.route('/review/<id>', methods=['PUT'])
def update_review(id):
    data = request.json
    result = db.review.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

@app.route('/review/<id>', methods=['DELETE'])
def delete_review(id):
    result = db.review.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})


# ------------------------ TIP ------------------------

@app.route('/tip', methods=['GET'])
def get_tips():
    tips = list(db.tip.find().limit(50))
    return jsonify([serialize_doc(t) for t in tips])

@app.route('/tip/<id>', methods=['GET'])
def get_tip(id):
    tip = db.tip.find_one({"_id": ObjectId(id)})
    if tip:
        return jsonify(serialize_doc(tip))
    return jsonify({"error": "Tip not found"}), 404

@app.route('/tip', methods=['POST'])
def create_tip():
    data = request.json
    result = db.tip.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})

@app.route('/tip/<id>', methods=['PUT'])
def update_tip(id):
    data = request.json
    result = db.tip.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

@app.route('/tip/<id>', methods=['DELETE'])
def delete_tip(id):
    result = db.tip.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})


# ------------------------ CHECKIN ------------------------

@app.route('/checkin', methods=['GET'])
def get_checkins():
    checkins = list(db.checkin.find().limit(50))
    return jsonify([serialize_doc(c) for c in checkins])

@app.route('/checkin/<id>', methods=['GET'])
def get_checkin(id):
    checkin = db.checkin.find_one({"_id": ObjectId(id)})
    if checkin:
        return jsonify(serialize_doc(checkin))
    return jsonify({"error": "Checkin not found"}), 404

@app.route('/checkin', methods=['POST'])
def create_checkin():
    data = request.json
    result = db.checkin.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)})

@app.route('/checkin/<id>', methods=['PUT'])
def update_checkin(id):
    data = request.json
    result = db.checkin.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

@app.route('/checkin/<id>', methods=['DELETE'])
def delete_checkin(id):
    result = db.checkin.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})


# ------------------------ MAIN ------------------------

if __name__ == '__main__':
    app.run(debug=True)
