import datetime
import secrets
import time
import os

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
        print(db.get_files(data["id"]))
        return jsonify(db.get_files(data["id"])), 200
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/download/<token>/<id_file>")  # Добавить проверку токена
def download(token, id_file):
    try:
        id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])["id"]
        db = DB("react_db")
        if db.check_download(id_file=id_file, id_user=id):
            file_path = db.get_file(id_file)[1]
            filepath = f'file/{file_path}'
            return send_file(filepath, as_attachment=True)
        else:
            return "Файл не найден", 404
    except FileNotFoundError:
        return "Файл не найден", 404


@app.route("/get_name_file", methods=["POST"])
def get_name_file():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        user_jwt = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=['HS256'])

        if db.select_by("id", user_jwt["id"]) is not None:
            data = db.get_file_name(data["idFile"])
            print(data)
            if data is not None:
                return jsonify({"fileName": data[0]}), 200
            else:
                return jsonify({"message": "файл не найден"}), 404
        else:
            return jsonify({"message": "пользователь не найден"}), 403
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/set_name_file", methods=["POST"])
def set_name_file():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        print(data)
        user_jwt = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=['HS256'])

        if db.select_by("id", user_jwt["id"]) is not None:
            old_data = db.get_file(data["idFile"])
            name = data["nameFile"]
            path = f"{name}.{old_data[1].split(".")[1]}"
            os.rename(f"file/{old_data[1]}", f"file/{path}")
            db.set_name(name, path, data["idFile"])
            return jsonify({"message": "Имя файла отредактировано"}), 200
        else:
            return jsonify({"message": "пользователь не найден"}), 403
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/get_access_list", methods=["POST"])
def get_access_list():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        user_jwt = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=["HS256"])

        if db.check_download(data["file_id"], user_jwt["id"]):
            user_list = db.get_access_download(data["file_id"], user_jwt["id"])

            new_list = []

            for i in user_list:
                new_list.append(db.select_by("id", i[0])[: 3])

            print(new_list)
            return jsonify({"user_list": new_list}), 200

        else:
            return jsonify({"message": "Недостаточно прав"}), 403
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/del_from_access_list", methods=["POST"])
def del_from_access_list():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        user_jwt = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=["HS256"])

        if db.check_download(data["file_id"], user_jwt["id"]):
            print(user_jwt["id"])
            print(data["file_id"])
            db.del_user_from_access_list(data["file_id"], data["user_id"])

            return jsonify({"message": "пользователь удален"}), 200
        else:
            return jsonify({"message": "Недостаточно прав"}), 403
    else:
        return jsonify({"message": "Неверный формат данных"}), 415


@app.route("/add_user_access_list", methods=["POST"])
def add_user_access_list():
    if request.is_json:
        db = DB("react_db")
        data = request.get_json()
        user_jwt = jwt.decode(data["token"], app.config["SECRET_KEY"], algorithms=["HS256"])

        if db.check_download(data["file_id"], user_jwt["id"]):
            user_add = db.select_by("email", data["email"])[:3]

            print(data["file_id"], user_add[0])
            db.add_user_access_list(data["file_id"], user_add[0])

            return jsonify({"new_user": user_add}), 200
        else:
            return jsonify({"message": "Недостаточно прав"}), 403
    else:
        return jsonify({"message": "Неверный формат данных"}), 415




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
