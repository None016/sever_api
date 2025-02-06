import datetime
import secrets
import time

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import jwt
from pyexpat.errors import messages

from DB import DB

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwer1234"
CORS(app)


@app.route('/reg', methods=['POST', 'GET']) # Убедитесь, что метод POST разрешен
def reg():
    if request.is_json:
        try:
            data = request.get_json()
            print(f"Полученные данные: {data}")
            db = DB("react_db")
            print(db.check_is_reg(data["email"]))
            if db.check_is_reg(data["email"]):
                return jsonify({"message": "пользователь уже зарегестрирован"}), 409
            else:
                db.set_user(data["name"], data["email"], data["password"])
                return jsonify({"message": "пользователь зарегестрирован"}), 200
        except:
            return jsonify({"messages": "Неверный формат данных"}), 415

  
@app.route("/aut", methods=["POST"])
def autorization():
    if request.is_json:
        try:
            db = DB("react_db")
            data = request.get_json()
            print(data)
            if db.check_is_aut(data["email"], data["password"]):
                print("___________________________")
                print(datetime.datetime.utcnow())
                token = jwt.encode({"id": db.select_by("email", data["email"])[0],
                                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)}, app.config['SECRET_KEY'])
                return jsonify({"message": "пользователь авторизован",
                                "token": token}), 200
            else:
                return jsonify({"message": "пользоваетель не авторизован"}), 409

        except:
            return jsonify({"message": "Неверный формат json"}), 415
    # session["id"] = db.get_users(data["email"])
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/verification", methods=["POST"])
def token_verification():
    if request.is_json:
        try:
            db = DB("react_db")
            data = request.get_json()
            print(data)
            data = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=['HS256'])
            print(data)
            if db.select_by("id", data["id"]) is not None:
                if int(data["exp"]) <= time.time():
                    return jsonify({"message": "время сеанса истекло"}), 401
                else:
                    print("все ок")
                    return jsonify({"message": "Пользователь авторизован"}), 200
            else:
                return jsonify({"message": "пользователь не найден"}), 409
        except:
            return jsonify({"message": "Неверный формат json"}), 415
    else:
        print("Неверный формат данных")
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/get_files", methods=["POST"])
def get_files():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        print(data)
        data = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=['HS256'])
        print(data)
        print(db.get_file(data["id"]))
        return jsonify(db.get_file(data["id"])), 200
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/download/<file_name>")
def download(file_name):
    try:
        filepath = f'file/{file_name}'
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return "Файл не найден", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
