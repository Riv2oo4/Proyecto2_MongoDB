
from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from flask_cors import CORS
from gridfs import GridFS

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://julio:Cesario2025@proyecto2.76c4wsh.mongodb.net/?retryWrites=true&w=majority&appName=proyecto2")
db = client['proyecto2']
fs = GridFS(db)

# Crear índices
db.business.create_index([("name", ASCENDING)])
db.user.create_index([("name", ASCENDING)])
db.review.create_index([("business_id", ASCENDING)])
db.tip.create_index([("user_id", ASCENDING)])
db.checkin.create_index([("business_id", ASCENDING)])

def serialize(doc):
    doc['_id'] = str(doc['_id'])
    return doc

# Funciones genéricas
def get_all(collection):
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))
    sort_field = request.args.get('sort', '_id')
    sort_order = ASCENDING if request.args.get('order', 'asc') == 'asc' else DESCENDING
    projection = {field: 1 for field in request.args.get('fields', '').split(',') if field}
    docs = list(db[collection].find({}, projection).sort(sort_field, sort_order).skip(skip).limit(limit))
    return jsonify([serialize(d) for d in docs])

def get_one(collection, id):
    doc = db[collection].find_one({"_id": ObjectId(id)})
    return jsonify(serialize(doc)) if doc else (jsonify({"error": "Not found"}), 404)

def insert_one(collection):
    data = request.json
    inserted = db[collection].insert_one(data)
    return jsonify({"inserted_id": str(inserted.inserted_id)})

def update_one(collection, id):
    data = request.json
    result = db[collection].update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"modified_count": result.modified_count})

def delete_one(collection, id):
    result = db[collection].delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted_count": result.deleted_count})

# CRUD para cada colección
@app.route('/business', methods=['GET', 'POST'])
def business_collection():
    if request.method == 'GET': return get_all('business')
    if request.method == 'POST': return insert_one('business')

@app.route('/business/<id>', methods=['GET', 'PUT', 'DELETE'])
def business_document(id):
    if request.method == 'GET': return get_one('business', id)
    if request.method == 'PUT': return update_one('business', id)
    if request.method == 'DELETE': return delete_one('business', id)

@app.route('/user', methods=['GET', 'POST'])
def user_collection():
    if request.method == 'GET': return get_all('user')
    if request.method == 'POST': return insert_one('user')

@app.route('/user/<id>', methods=['GET', 'PUT', 'DELETE'])
def user_document(id):
    if request.method == 'GET': return get_one('user', id)
    if request.method == 'PUT': return update_one('user', id)
    if request.method == 'DELETE': return delete_one('user', id)

@app.route('/review', methods=['GET', 'POST'])
def review_collection():
    if request.method == 'GET': return get_all('review')
    if request.method == 'POST': return insert_one('review')

@app.route('/review/<id>', methods=['GET', 'PUT', 'DELETE'])
def review_document(id):
    if request.method == 'GET': return get_one('review', id)
    if request.method == 'PUT': return update_one('review', id)
    if request.method == 'DELETE': return delete_one('review', id)

@app.route('/tip', methods=['GET', 'POST'])
def tip_collection():
    if request.method == 'GET': return get_all('tip')
    if request.method == 'POST': return insert_one('tip')

@app.route('/tip/<id>', methods=['GET', 'PUT', 'DELETE'])
def tip_document(id):
    if request.method == 'GET': return get_one('tip', id)
    if request.method == 'PUT': return update_one('tip', id)
    if request.method == 'DELETE': return delete_one('tip', id)

@app.route('/checkin', methods=['GET', 'POST'])
def checkin_collection():
    if request.method == 'GET': return get_all('checkin')
    if request.method == 'POST': return insert_one('checkin')

@app.route('/checkin/<id>', methods=['GET', 'PUT', 'DELETE'])
def checkin_document(id):
    if request.method == 'GET': return get_one('checkin', id)
    if request.method == 'PUT': return update_one('checkin', id)
    if request.method == 'DELETE': return delete_one('checkin', id)

# Agregación: top 5 negocios con más reviews
@app.route('/aggregations/top-reviewed-businesses')
def top_reviewed_businesses():
    pipeline = [
        {"$group": {"_id": "$business_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "business",
            "localField": "_id",
            "foreignField": "_id",
            "as": "business_info"
        }}
    ]
    result = list(db.review.aggregate(pipeline))
    return jsonify(result)

# Consulta con arrays
@app.route('/tips-with-compliments')
def tips_with_compliments():
    tips = list(db.tip.find({"compliment_count": {"$gt": 1}}).limit(20))
    return jsonify([serialize(t) for t in tips])

# GridFS subir
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_id = fs.put(file, filename=file.filename)
    return jsonify({"file_id": str(file_id)})

# GridFS descargar
@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file = fs.get(ObjectId(file_id))
    return app.response_class(file.read(), content_type='application/octet-stream')

@app.route('/status')
def status():
    return jsonify({"status": "API running with full rubric support"})

if __name__ == '__main__':
    app.run(debug=True)
