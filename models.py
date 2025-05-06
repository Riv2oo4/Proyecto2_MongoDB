# models.py

from bson import ObjectId

class Usuario:
    def __init__(self, nombre, correo, direccion):
        self.nombre = nombre
        self.correo = correo
        self.direccion = direccion

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "correo": self.correo,
            "direccion": self.direccion
        }

class Restaurante:
    def __init__(self, nombre, direccion, ubicacion, categoria):
        self.nombre = nombre
        self.direccion = direccion
        self.ubicacion = ubicacion  # { "type": "Point", "coordinates": [long, lat] }
        self.categoria = categoria  # ej. Mexicano, Pizza, etc.

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "direccion": self.direccion,
            "ubicacion": self.ubicacion,
            "categoria": self.categoria
        }

class ArticuloMenu:
    def __init__(self, restaurante_id, nombre, descripcion, precio):
        self.restaurante_id = ObjectId(restaurante_id)
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

    def to_dict(self):
        return {
            "restaurante_id": self.restaurante_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio
        }

class Orden:
    def __init__(self, usuario_id, restaurante_id, items, estado, total):
        self.usuario_id = ObjectId(usuario_id)
        self.restaurante_id = ObjectId(restaurante_id)
        self.items = items  # Lista de objetos: {articulo_id, cantidad}
        self.estado = estado  # ej. pendiente, en preparación, entregado
        self.total = total

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "restaurante_id": self.restaurante_id,
            "items": self.items,
            "estado": self.estado,
            "total": self.total
        }

class Reseña:
    def __init__(self, usuario_id, restaurante_id, orden_id, calificacion, comentario):
        self.usuario_id = ObjectId(usuario_id)
        self.restaurante_id = ObjectId(restaurante_id)
        self.orden_id = ObjectId(orden_id)
        self.calificacion = calificacion  # de 1 a 5
        self.comentario = comentario

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "restaurante_id": self.restaurante_id,
            "orden_id": self.orden_id,
            "calificacion": self.calificacion,
            "comentario": self.comentario
        }
