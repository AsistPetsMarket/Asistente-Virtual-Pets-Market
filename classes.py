class Question:
    id = 0
    text = ""
    estado = 1
    options = []
    id_sintoma = 0
    sympton = None

    def __init__(self, id, text, estado, options, id_sintoma, sympton):
        self.id = id
        self.text = text
        self.options = options
        self.estado = estado
        self.id_sintoma = id_sintoma
        self.sympton = sympton

    def __str__(self):
        return self.text + " " + str(self.estado) + " " + str(self.options)

    def __repr__(self):
        return self.text + " " + str(self.estado) + " " + str(self.options)

    def __eq__(self, value):
        return self.id == value.id

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "options": [option.to_dict() for option in self.options],
            "estado": self.estado,
            "id_sintoma": self.id_sintoma,
            "symptom": self.sympton.to_dict()
        }


class Options:
    id = 0
    text = ""
    estado = 1
    id_pregunta = 0
    estado_validacion = 0

    def __init__(self, id, text, estado, id_pregunta, estado_validacion):
        self.id = id
        self.text = text
        self.estado = estado
        self.id_pregunta = id_pregunta
        self.estado_validacion = estado_validacion

    def __str__(self):
        return self.text + " "  + " " + str(self.estado) + " " + str(self.id_pregunta)

    def __repr__(self):
        return self.text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "estado": self.estado,
            "id_pregunta": self.id_pregunta,
            "estado_validacion": self.estado_validacion
        }

class Symptom:
    id = 0
    nombre = ""
    estado = 1

    def __init__(self, id, nombre, estado):
        self.id = id
        self.nombre = nombre
        self.estado = estado

    def __str__(self):
        return self.nombre + " " + str(self.estado)

    def __repr__(self):
        return self.nombre

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "estado": self.estado
        }

class User:
    id = 0
    nombre = ""
    apellido = ""
    direccion = ""
    telefono = ""
    email = ""
    edad = 0
    sexo = ""
    cedula = ""
    nacionalidad = ""
    clave = ""
    estado = 1

    def __init__(self, id, nombre, apellido, direccion, telefono, email, edad, sexo, cedula, nacionalidad, clave, estado):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.edad = edad
        self.sexo = sexo
        self.cedula = cedula
        self.nacionalidad = nacionalidad
        self.clave = clave
        self.estado = estado

    def __str__(self):
        return self.nombre + " " + self.apellido + " " + self.direccion + " " + self.email + " " + str(self.edad) + " " + self.sexo + " " + self.cedula + " " + self.nacionalidad + " " + self.clave + " " + str(self.estado)

    def __repr__(self):
        return self.nombre + " " + self.apellido

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "email": self.email,
            "edad": self.edad,
            "sexo": self.sexo,
            "cedula": self.cedula,
            "nacionalidad": self.nacionalidad,
            "estado": self.estado
        }