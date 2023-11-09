# views.py

from flask import request, render_template, redirect, url_for, session, make_response
from app import app

import json
import datetime

with open("users.json", "r") as file:
    users = json.load(file)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("info"))

    return render_template("login.html")

@app.route("/info", methods=["GET", "POST"])
def info():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    saved_cookies = request.cookies.items()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_cookie":
            key = request.form.get("key")
            value = request.form.get("value")
            expiration_time = request.form.get("expiration_time")

            if key and value and expiration_time:
                expiration_time = int(expiration_time)
                expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=expiration_time)
                response = make_response(render_template("info.html", username=username, cookies=saved_cookies))
                response.set_cookie(key, value, expires=expiration_date)
                message = f"Cookie '{key}' додано успішно."
                return response

            else:
                message = "Будь ласка, заповніть всі поля."

        elif action == "delete_cookie":
            key_to_delete = request.form.get("key_to_delete")

            if key_to_delete:
                response = make_response(render_template("info.html", username=username, cookies=saved_cookies))
                response.delete_cookie(key_to_delete)
                message = f"Cookie '{key_to_delete}' видалено успішно."
                return response

            else:
                response = make_response(render_template("info.html", username=username, cookies=saved_cookies))
                for key in request.cookies.keys():
                    response.delete_cookie(key)
                message = "Всі кукі видалено успішно."
                return response

        else:
            message = "Невідома дія."

    return render_template("info.html", username=username, cookies=saved_cookies)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/change_password", methods=["POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    new_password = request.form.get("new_password")

    users[username] = new_password

    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

    message = "Пароль змінено успішно."
    return render_template("info.html", username=username, message=message, cookies=request.cookies.items())
