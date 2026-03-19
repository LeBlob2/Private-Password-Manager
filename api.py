import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from create_open_database import (
    get_connection,
    fetch_all_passwords,
    list_databases,
    resolve_db_path
)

app = Flask(__name__)
CORS(app, origins="moz-extension://*")

# Holds open connections keyed by db_name
_sessions: dict[str, object] = {}


@app.route("/databases", methods=["GET"])
def databases():
    return jsonify(list_databases())


@app.route("/unlock", methods=["POST"])
def unlock():
    data        = request.get_json()
    db_name     = data.get("db_name", "")
    password    = data.get("password", "")

    if not db_name or not password:
        return jsonify({"error": "db_name and password are required"}), 400

    db_path = resolve_db_path(db_name)
    if not os.path.exists(db_path):
        return jsonify({"error": f'Database "{db_name}" not found'}), 404

    try:
        conn = get_connection(password, db_path)
        _sessions[db_name] = conn
        return jsonify({"ok": True})
    except ValueError:
        return jsonify({"error": "Wrong password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch", methods=["GET"])
def fetch():
    db_name = request.args.get("db_name", "")
    if not db_name:
        return jsonify({"error": "db_name is required"}), 400
    if db_name not in _sessions:
        return jsonify({"error": "Not unlocked"}), 403

    try:
        rows = fetch_all_passwords(_sessions[db_name])
        entries = [
            {
                "id":         row[0],
                "website":    row[1],
                "username":   row[2],
                "email":      row[3],
                "password":   row[4],
                "created_at": row[5]
            }
            for row in rows
        ]
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/lock", methods=["POST"])
def lock():
    data    = request.get_json()
    db_name = data.get("db_name", "")
    if db_name in _sessions:
        _sessions[db_name].close()
        del _sessions[db_name]
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(port=5000, debug=False)
