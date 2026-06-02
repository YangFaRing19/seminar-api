from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def create_database():

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_general_ci
    """)

    conn.commit()

    cursor.close()
    conn.close()

def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    # rooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            capacity INT NOT NULL,
            equipment VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # reservations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id INT NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            user_email VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            purpose VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_reservations_room
                FOREIGN KEY (room_id) REFERENCES rooms(id)
                ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()

    cursor.close()
    conn.close()

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route("/api/rooms", methods=["GET"])
def get_rooms():

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM rooms")
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "items": items,
        "count": len(items)
    })

@app.route("/api/rooms/<int:room_id>", methods=["GET"])
def get_room(room_id):

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM rooms WHERE id=%s",
        (room_id,)
    )

    room = cursor.fetchone()

    cursor.close()
    conn.close()

    if room is None:
        return jsonify({"message": "room not found"}), 404

    return jsonify(room)

@app.route("/api/rooms", methods=["POST"])
def create_room():

    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO rooms
        (name, capacity, equipment)
        VALUES (%s, %s, %s)
        """,
        (
            data["name"],
            data["capacity"],
            data.get("equipment", "")
        )
    )

    conn.commit()

    room_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id": room_id,
        "message": "created"
    }), 201

@app.route("/api/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):

    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE rooms
        SET
            name=%s,
            capacity=%s,
            equipment=%s
        WHERE id=%s
        """,
        (
            data["name"],
            data["capacity"],
            data.get("equipment", ""),
            room_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "id": room_id,
        "message": "updated"
    })

@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM rooms WHERE id=%s",
        (room_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "id": room_id,
        "message": "deleted"
    })

@app.route("/api/reservations", methods=["GET"])
def get_reservations():

    room_id = request.args.get("room_id")
    date = request.args.get("date")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM reservations
        WHERE 1=1
    """

    params = []

    if room_id:
        sql += " AND room_id=%s"
        params.append(room_id)

    if date:
        sql += ' AND date="%s"'
        params.append(date)

    cursor.execute(sql, tuple(params))

    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "items": items,
        "count": len(items)
    })

@app.route("/api/reservations", methods=["POST"])
def create_reservation():

    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reservations
        (
            room_id,
            user_name,
            user_email,
            date,
            start_time,
            end_time,
            purpose
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            data["room_id"],
            data["user_name"],
            data["user_email"],
            data["date"],
            data["start_time"],
            data["end_time"],
            data.get("purpose", "")
        )
    )

    conn.commit()

    reservation_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id": reservation_id,
        "message": "reserved"
    }), 201

@app.route("/api/reservations/<int:reservation_id>", methods=["DELETE"])
def delete_reservation(reservation_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM reservations WHERE id=%s",
        (reservation_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "id": reservation_id,
        "message": "cancelled"
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

create_tables()

if __name__ == "__main__":
    app.run(debug=True)