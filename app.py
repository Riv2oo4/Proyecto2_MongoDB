
from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING,TEXT , InsertOne, UpdateOne, DeleteOne, UpdateMany, DeleteMany
import json
from bson import ObjectId
from flask_cors import CORS
from gridfs import GridFS

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://julio:Cesario2025@proyecto2.76c4wsh.mongodb.net/?retryWrites=true&w=majority&appName=proyecto2")
db = client['proyecto2']
fs = GridFS(db)


#índices simples
# Usuarios
db.user.create_index([("name", ASCENDING)])
# Negocios
db.business.create_index([("name", ASCENDING)])
# Reviews
db.review.create_index([("stars", ASCENDING)])

#índices compuestos
# Reviews: índice compuesto por user y business
db.review.create_index([("user_id", ASCENDING), ("business_id", ASCENDING)])

# Tips: índice compuesto por user y date
db.tip.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
#ÍNDICE MULTIKEY
# Business: índice multikey en arreglo categories
db.business.create_index([("categories", ASCENDING)])



#índices de texto
# Review: índice de texto en el campo "text"
db.review.create_index([("text", TEXT)])

# Business: búsquedas por categorías 
db.business.create_index([("categories", TEXT)])

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

@app.route('/business/<id>', methods=['GET', 'PUT', 'DELETE'])
def business_document(id):
    if request.method == 'GET': return get_one('business', id)
    if request.method == 'PUT': return update_one('business', id)
    if request.method == 'DELETE': return delete_one('business', id)

@app.route('/user/<id>', methods=['GET', 'PUT', 'DELETE'])
def user_document(id):
    if request.method == 'GET': return get_one('user', id)
    if request.method == 'PUT': return update_one('user', id)
    if request.method == 'DELETE': return delete_one('user', id)

@app.route('/review/<id>', methods=['GET', 'PUT', 'DELETE'])
def review_document(id):
    if request.method == 'GET': return get_one('review', id)
    if request.method == 'PUT': return update_one('review', id)
    if request.method == 'DELETE': return delete_one('review', id)

@app.route('/tip/<id>', methods=['GET', 'PUT', 'DELETE'])
def tip_document(id):
    if request.method == 'GET': return get_one('tip', id)
    if request.method == 'PUT': return update_one('tip', id)
    if request.method == 'DELETE': return delete_one('tip', id)

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

@app.route('/verificar-indices/<coleccion>', methods=['GET'])
def verificar_indices(coleccion):
    try:
        indices = list(db[coleccion].list_indexes())
        return jsonify([{
            "name": idx["name"],
            "key": list(idx["key"].items()),
            "type": idx.get("2dsphereIndexVersion", "normal") if "2dsphereIndexVersion" in idx else "normal"
        } for idx in indices])
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/restaurantes-cercanos', methods=['GET'])
def restaurantes_cercanos():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        max_dist = int(request.args.get('max_dist', 1000))  

        resultados = db.business.find({
            "ubicacion": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": max_dist
                }
            }
        }).limit(10)

        return jsonify([serialize(r) for r in resultados])
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/ubicaciones-restaurantes', methods=['GET'])
def ubicaciones_restaurantes():
    restaurantes = db.business.find(
        {"ubicacion": {"$exists": True}},
        {"name": 1, "ubicacion": 1, "_id": 0}
    )
    return jsonify(list(restaurantes))

@app.route('/agregar-ubicacion/<id>', methods=['PUT'])
def agregar_ubicacion(id):
    try:
        lon = float(request.args.get('lon'))
        lat = float(request.args.get('lat'))

        result = db.business.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "ubicacion": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                }
            }
        )
        return jsonify({"modified_count": result.modified_count})
    except Exception as e:
        return jsonify({"error": str(e)})
import random

@app.route('/agregar-ubicaciones-multiples', methods=['PUT'])
def agregar_ubicaciones_multiples():
    try:
        base_lon = -75.1652
        base_lat = 39.9526

        restaurantes = db.business.find().limit(50)  

        updated = 0
        for restaurante in restaurantes:
            lon = base_lon + random.uniform(-0.01, 0.01)
            lat = base_lat + random.uniform(-0.01, 0.01)

            result = db.business.update_one(
                {"_id": restaurante["_id"]},
                {
                    "$set": {
                        "ubicacion": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        }
                    }
                }
            )

            if result.modified_count > 0:
                updated += 1

        return jsonify({"ubicaciones_agregadas": updated})
    except Exception as e:
        return jsonify({"error": str(e)})
    
    
@app.route('/agregar-ubicaciones-guatemala', methods=['PUT'])
def agregar_ubicaciones_guatemala():
    try:
        base_lon = -90.5069
        base_lat = 14.6349

        restaurantes = db.business.find().limit(50)  

        updated = 0
        for restaurante in restaurantes:
            lon = base_lon + random.uniform(-0.01, 0.01)
            lat = base_lat + random.uniform(-0.01, 0.01)

            result = db.business.update_one(
                {"_id": restaurante["_id"]},
                {
                    "$set": {
                        "ubicacion": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        }
                    }
                }
            )

            if result.modified_count > 0:
                updated += 1

        return jsonify({"ubicaciones_agregadas": updated})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/restaurantes/total', methods=['GET'])
def contar_restaurantes():
    total = db.business.count_documents({
        "categories": {
            "$regex": ".*Restaurants.*",
            "$options": "i"
        }
    })
    return jsonify({"total_restaurantes": total})


@app.route('/restaurantes', methods=['GET'])
def obtener_restaurantes():
    restaurantes = db.business.find(
        { "categories": { "$regex": ".*Restaurants.*", "$options": "i" } },
        { "name": 1, "address": 1, "city": 1, "state": 1, "categories": 1, "_id": 0 }
    ).limit(100)  # Puedes ajustar o paginar si hay muchos
    return jsonify(list(restaurantes))

@app.route('/<collection>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_collection(collection):
    coll = db[collection]

    # GET con filtros, proyección, sort, skip, limit
    if request.method == 'GET':
        filt   = json.loads(request.args.get('filter', '{}'))
        proj   = json.loads(request.args.get('projection', '{}'))
        sort   = json.loads(request.args.get('sort', '[]'))
        skip   = int(request.args.get('skip', 0))
        limit  = int(request.args.get('limit', 50))

        cursor = coll.find(filt, proj)
        if sort:  cursor = cursor.sort(sort)
        if skip:  cursor = cursor.skip(skip)
        if limit: cursor = cursor.limit(limit)
        return jsonify([serialize(d) for d in cursor])

    # POST/PUT/DELETE con bulk_write
    data = request.json
    ops  = []

    if request.method == 'POST':
        if isinstance(data, list):
            ops += [InsertOne(doc) for doc in data]
        else:
            ops.append(InsertOne(data))

    elif request.method == 'PUT':
        updates = data if isinstance(data, list) else [data]
        for u in updates:
            filt   = u.get('filter', {})
            update = u.get('update', {})
            if u.get('many', False):
                ops.append(UpdateMany(filt, update))
            else:
                ops.append(UpdateOne(filt, update))

    elif request.method == 'DELETE':
        deletes = data if isinstance(data, list) else [data]
        for d in deletes:
            filt = d.get('filter', {})
            if d.get('many', False):
                ops.append(DeleteMany(filt))
            else:
                ops.append(DeleteOne(filt))

    if not ops:
        return jsonify({'error': 'No operations provided'}), 400

    result = coll.bulk_write(ops)
    return jsonify({
        'inserted_count': getattr(result, 'inserted_count', 0),
        'matched_count':  getattr(result, 'matched_count', 0),
        'modified_count': getattr(result, 'modified_count', 0),
        'deleted_count':  getattr(result, 'deleted_count', 0),
        'upserted_count': getattr(result, 'upserted_count', 0),
        'upserted_ids':   getattr(result, 'upserted_ids', {})
    }), 200
# Agregación simple: contar reviews por estrellas
@app.route('/aggregations/count-reviews-by-stars', methods=['GET'])
def count_reviews_by_stars():
    stars_values = db.review.distinct("stars")
    result = {}
    
    for star in stars_values:
        count = db.review.count_documents({"stars": star})
        result[str(star)] = count
    
    return jsonify(result)

# Agregación simple: contar usuarios por ciudad
@app.route('/aggregations/count-users-by-city', methods=['GET'])
def count_users_by_city():
    cities = db.user.distinct("cool")
    result = {}
    
    for city in cities:
        if city:  
            count = db.user.count_documents({"cool": city})
            result[city] = count
    
    return jsonify({"Personas mas cool": result})

# Agregación simple: categorías distintas de negocios
@app.route('/aggregations/distinct-business-categories', methods=['GET'])
def distinct_business_categories():
    categories = db.business.distinct("categories")
    categories = [cat for cat in categories if cat]
    categories.sort()
    
    return jsonify({"distinct_categories": categories})

# Agregación simple: contar tips por usuario
@app.route('/aggregations/count-tips-by-user/<user_id>', methods=['GET'])
def count_tips_by_user(user_id):
    try:
        user_id_obj = ObjectId(user_id) if len(user_id) == 24 else user_id
        
        count = db.tip.count_documents({"user_id": user_id_obj})
        
        user = db.user.find_one({"_id": user_id_obj}, {"name": 1})
        
        return jsonify({
            "user_id": user_id,
            "user_name": user.get("name", "Unknown") if user else "Unknown",
            "tips_count": count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Agregar una nueva categoría a un negocio usando $addToSet
@app.route('/business/convert-categories-to-array/<id>', methods=['PUT'])
def convert_categories_to_array(id):
    try:
        business = db.business.find_one({"_id": ObjectId(id)})
        
        if not business:
            return jsonify({"error": "Negocio no encontrado"}), 404
        
        if 'categories' in business and isinstance(business['categories'], str):
            categories_array = [business['categories']]
            
            result = db.business.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"categories": categories_array}}
            )
            
            return jsonify({
                "modified_count": result.modified_count,
                "message": "Campo 'categories' convertido de string a array"
            })
        elif 'categories' not in business:
            result = db.business.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"categories": []}}
            )
            
            return jsonify({
                "modified_count": result.modified_count,
                "message": "Campo 'categories' creado como array vacío"
            })
        else:
            return jsonify({
                "message": "El campo 'categories' ya es un array o tiene otro tipo"
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar una categoría de un negocio usando $pull
@app.route('/business/remove-category/<id>', methods=['PUT'])
def remove_business_category(id):
    try:
        category = request.json.get('category')
        if not category:
            return jsonify({"error": "Se requiere una categoría"}), 400
        
        result = db.business.update_one(
            {"_id": ObjectId(id)},
            {"$pull": {"categories": category}}
        )
        
        return jsonify({
            "modified_count": result.modified_count,
            "message": f"Categoría '{category}' eliminada del negocio" if result.modified_count > 0 else "No se realizaron cambios"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Agregar un nuevo horario a un negocio usando $push
@app.route('/business/add-hours/<id>', methods=['PUT'])
def add_business_hours(id):
    try:
        hours_data = request.json
        if not hours_data or not isinstance(hours_data, dict):
            return jsonify({"error": "Se requiere un objeto con el día y las horas"}), 400
        
        # Ejemplo: {"day": "Monday", "hours": "9:00-18:00"}
        result = db.business.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"hours": hours_data}}
        )
        
        return jsonify({
            "modified_count": result.modified_count,
            "message": "Horario agregado al negocio" if result.modified_count > 0 else "No se realizaron cambios"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Agregar múltiples categorías de una vez usando $each con $push
@app.route('/business/add-multiple-categories/<id>', methods=['PUT'])
def add_multiple_categories(id):
    try:
        categories = request.json.get('categories', [])
        if not categories or not isinstance(categories, list):
            return jsonify({"error": "Se requiere una lista de categorías"}), 400
        
        result = db.business.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"categories": {"$each": categories}}}
        )
        
        return jsonify({
            "modified_count": result.modified_count,
            "categories_added": len(categories),
            "message": "Categorías agregadas al negocio" if result.modified_count > 0 else "No se realizaron cambios"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Agregar un elemento a un array si no existe, o incrementar un contador si existe
@app.route('/user/add-favorite/<id>', methods=['PUT'])
def add_user_favorite(id):
    try:
        business_id = request.json.get('business_id')
        if not business_id:
            return jsonify({"error": "Se requiere un ID de negocio"}), 400
        
        # Primero verificamos si el array de favoritos existe
        user = db.user.find_one({"_id": ObjectId(id)})
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Si el usuario no tiene un array de favoritos, lo creamos con $set
        if "favorites" not in user:
            db.user.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"favorites": []}}
            )
        
        # Ahora agregamos el negocio a favoritos si no existe
        result = db.user.update_one(
            {"_id": ObjectId(id)},
            {"$addToSet": {"favorites": business_id}}
        )
        
        # Si se modificó, significa que se agregó a favoritos
        if result.modified_count > 0:
            # Incrementamos el contador de favoritos del negocio
            db.business.update_one(
                {"_id": ObjectId(business_id)},
                {"$inc": {"favorite_count": 1}}
            )
            
            return jsonify({
                "message": "Negocio agregado a favoritos"
            })
        else:
            return jsonify({
                "message": "El negocio ya estaba en favoritos"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar elementos específicos de un array usando $[]
@app.route('/business/update-hours/<id>', methods=['PUT'])
def update_business_hours(id):
    try:
        day = request.json.get('day')
        new_hours = request.json.get('hours')
        
        if not day or not new_hours:
            return jsonify({"error": "Se requiere el día y las nuevas horas"}), 400
        
        result = db.business.update_one(
            {
                "_id": ObjectId(id),
                "hours.day": day
            },
            {
                "$set": {"hours.$[elem].hours": new_hours}
            },
            array_filters=[{"elem.day": day}]
        )
        
        return jsonify({
            "modified_count": result.modified_count,
            "message": f"Horario actualizado para {day}" if result.modified_count > 0 else "No se encontró el día especificado"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True)
