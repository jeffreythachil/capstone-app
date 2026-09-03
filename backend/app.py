from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


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