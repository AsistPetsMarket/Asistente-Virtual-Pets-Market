import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS  # Importa CORS
from collections import defaultdict

import joblib
import pandas as pd
import numpy as np
import json
from werkzeug.security import generate_password_hash, check_password_hash
from classes import Options, Question, User, Symptom

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir solicitudes desde cualquier origen

app.config['MYSQL_HOST'] = '34.135.24.52'
app.config['MYSQL_USER'] = 'Admin'
app.config['MYSQL_PASSWORD'] = 'Juandiego12'
app.config['MYSQL_DB'] = 'u783914092_petsmarket'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento"

# Cargar el modelo y el LabelEncoder al iniciar la aplicación
try:
    modelo_cargado = joblib.load("modelo_random_forest.pkl")
    label_encoder_cargado = joblib.load("label_encoder.pkl")
    print("Modelo y codificador cargados correctamente.")
except FileNotFoundError:
    print("Error: Archivos del modelo no encontrados.")
    exit()
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()


def normalize_feature_name(name):
    """Normaliza el nombre del síntoma para coincidir con el modelo entrenado"""
    return name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

def normalize_feature_name(name):
    """Normaliza el nombre del síntoma para coincidir con el modelo entrenado"""
    return name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

def preprocesar_entrada(datos_usuario):
    try:
        # Normalizar los nombres de las características
        datos_normalizados = {normalize_feature_name(key): value for key, value in datos_usuario.items()}

        # Cargar el modelo para obtener los nombres de las características esperadas
        modelo = joblib.load('modelo_random_forest.pkl')
        feature_names = modelo.feature_names_in_

        # Crear un diccionario con todas las características que el modelo espera
        entrada_completa = {feature: datos_normalizados.get(feature, 0) for feature in feature_names}

        # Verificar si hay columnas faltantes
        columnas_faltantes = [feature for feature in feature_names if feature not in datos_normalizados]
        if columnas_faltantes:
            print(f"Advertencia: Columnas faltantes en los datos de entrada: {columnas_faltantes}")

        # Convertir a DataFrame
        entrada_df = pd.DataFrame([entrada_completa])

        # Asegurarse de que todos los valores sean numéricos
        entrada_df = entrada_df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Depuración: Mostrar la entrada preprocesada
        print("Entrada preprocesada para el modelo:")
        print(entrada_df)

        # Verificar los valores únicos de cada columna
        print("Valores únicos por columna:")
        print(entrada_df.nunique())

        # Verificar que el número de columnas coincida
        print(f"Número de columnas esperadas: {len(feature_names)}")
        print(f"Número de columnas recibidas: {len(entrada_df.columns)}")
        print(f"Coincidencia de columnas: {set(feature_names) == set(entrada_df.columns)}")

        return entrada_df
    except ValueError:
        print("Error: Datos de entrada inválidos. Asegúrate de que sean numéricos.")
        return None
    except KeyError as e:
        print(f"Error: falta la columna {e} en los datos de entrada")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None



@app.route('/predecir', methods=['POST'])
def predecir():
    try:
        datos_usuario = request.get_json()
        entrada_preprocesada = preprocesar_entrada(datos_usuario)

        if entrada_preprocesada is None:
            return jsonify({'error': 'Datos de entrada inválidos'}), 400

        predicciones_prob = modelo_cargado.predict_proba(entrada_preprocesada)
        prediccion_numerica = np.argmax(predicciones_prob, axis=1)
        prediccion_etiqueta = label_encoder_cargado.inverse_transform(prediccion_numerica)
        confianza = np.max(predicciones_prob, axis=1)
        name = prediccion_etiqueta[0]

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cab_diagnostico cd JOIN tratamiento tr on tr.id_diagnostico = cd.id_diagnostico WHERE cd.label = %s", (name,))
        tratamientos = cursor.fetchall()
        cursor.close()

        tratamientosData = []
        resultado = ""
        for tratamiento in tratamientos:
            print(tratamiento)
            tratamientosData.append({
                "tratamiento": tratamiento[5]
            })
            resultado = tratamiento[1]

        return jsonify({"resultado": resultado, "confianza": float(confianza[0]), "tratamientos": tratamientosData}), 200

    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = json.loads(request.data)
        cedula = data.get("cedula")
        password = data.get('password')

        if not cedula or not password:
            return jsonify({"message": "Cedula and password are required"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cliente WHERE cedula = %s", (cedula,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[10], password):
            customUser = User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9], user[10], user[11])
            return jsonify(customUser.to_dict()), 200
        else:
            return jsonify({"message": "Invalid cedula or password"}), 401

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = json.loads(request.data)
        nombre = data.get("nombre")
        apellido = data.get("apellido")
        direccion = data.get("direccion")
        telefono = data.get("telefono")
        email = data.get("correo")
        edad = data.get("edad")
        sexo = data.get("sexo")
        cedula = data.get("cedula")
        nacionalidad = data.get("nacionalidad")
        password = data.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * from cliente WHERE cedula = %s", (cedula,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            return jsonify({"message": "User already exists"}), 400

        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO cliente (nombre, apellido, direccion, telf, correo, edad, sexo, cedula, nacionalidad, clave, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, apellido, direccion, telefono, email, edad, sexo, cedula, nacionalidad, hashed_password, 1))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Registration successful"}), 200

    except Exception as e:
        print("ERROR", e)
        return jsonify({'error': 'Error interno del servidor al registrar un cliente'}), 500

@app.route("/init", methods=["GET"])
def initConversation():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM cab_pregunta cp JOIN respuesta re on re.id_pregunta = cp.id_pregunta JOIN sintoma si on si.id_sintoma = cp.id_sintoma")
        results = list(cursor.fetchall())

        questions = {}
        options = []
        for result in results:
            sympton = Symptom(result[9], result[10], result[11])
            question = Question(result[0], result[1], result[2], [], result[3], sympton)
            option = Options(result[4], result[5], result[6], result[7], result[8])
            if question.id not in questions:
                questions[question.id] = question
            options.append(option)

        grouped_options = defaultdict(list)
        for option in options:
            grouped_options[option.id_pregunta].append(option)

        for key in grouped_options:
            questions[key].options = grouped_options[key]

        return jsonify([item.to_dict() for item in questions.values()]), 200

    except Exception as e:
        print("ERROR", e)
        return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
