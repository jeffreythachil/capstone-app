from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import boto3
import json
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DB_SECRET_NAME = os.getenv("DB_SECRET_NAME", "capstone/database")


def get_database_credentials():
    """
    Retrieve database credentials from AWS Secrets Manager.

    For local development and CI tests, DB_USER and DB_PASSWORD
    environment variables can still be supplied directly.
    In EKS production, the application retrieves them from
    AWS Secrets Manager using EKS Pod Identity.
    """

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if db_user and db_password:
        return db_user, db_password

    client = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION
    )

    response = client.get_secret_value(
        SecretId=DB_SECRET_NAME
    )

    secret_string = response.get("SecretString")

    if not secret_string:
        raise RuntimeError(
            "AWS Secrets Manager secret does not contain SecretString"
        )

    secret = json.loads(secret_string)

    db_user = secret.get("username")
    db_password = secret.get("password")

    if not db_user or not db_password:
        raise RuntimeError(
            "AWS Secrets Manager secret must contain "
            "'username' and 'password'"
        )

    return db_user, db_password


def get_db_connection():
    db_user, db_password = get_database_credentials()

    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    if not db_host:
        raise RuntimeError("DB_HOST environment variable is required")

    if not db_name:
        raise RuntimeError("DB_NAME environment variable is required")

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )


@app.route("/", methods=["GET"])
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/style.css", methods=["GET"])
def style():
    return send_from_directory("../frontend", "style.css")


@app.route("/script.js", methods=["GET"])
def script():
    return send_from_directory("../frontend", "script.js")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/api/documents", methods=["GET"])
def get_documents():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, category, description, file_name, created_at
        FROM documents
        ORDER BY created_at DESC
    """)

    documents = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(documents)


@app.route("/api/documents", methods=["POST"])
def add_document():

    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    file = request.files.get("file")

    if not name:
        return jsonify({
            "error": "Document name is required"
        }), 400

    if not file:
        return jsonify({
            "error": "File is required"
        }), 400

    file_name = file.filename

    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    file.save(file_path)

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO documents
        (name, category, description, file_name)
        VALUES (%s, %s, %s, %s)
    """, (name, category, description, file_name))

    connection.commit()

    document_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Document added successfully",
        "id": document_id,
        "file_name": file_name
    }), 201


@app.route("/api/documents/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM documents WHERE id = %s",
        (document_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Document not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Document deleted successfully"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
