from flask import Flask, render_template, request, redirect,url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy


DEBUG = True
SECRET_KEY = 'bfbnm3444f39619e2dfsdfddfdsa3b55wrbafgh228desdfeb124466cbe5c75'
SQLALCHEMY_DATABASE_URI = "sqlite:///weather.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
#API_key = "190a5f317f078959551b58f2f5e7b31b"
app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)


@app.route("/")
def index_get():
    cities = City.query.all()
    #url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&&appid=190a5f317f078959551b58f2f5e7b31b"

    weather_data = []
    for city in cities:
        r = get_weather_data(city.name)

        weather ={
            "city":r["name"],
            "temperature":r["main"]["temp"],
            "description":r["weather"][0]["description"],
            "icon":r["weather"][0]["icon"]
        }

        weather_data.append(weather)

    return render_template("weather.html", weather_data = weather_data)


def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&&appid=190a5f317f078959551b58f2f5e7b31b"
    r = requests.get(url).json()
    return r

@app.route("/", methods = ["POST"])
def index_post():
    new_city = request.form.get("city").capitalize()
    if new_city:
        existing_city = City.query.filter_by(name = new_city).first()
        if not existing_city:
            weather_data = get_weather_data(new_city)
            if weather_data["cod"] == 200:

                new_city_obj = City(name = new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err = "City doesn't exist"
                flash(message=err, category="error")
        else:
            err = "this city is already added"
            flash(message=err, category="warning")

    return redirect(url_for("index_get"))

@app.route("/delete/<name>")
def delete(name):
    city = City.query.filter_by(name = name).first()
    print(city)
    db.session.delete(city)
    db.session.commit()

    flash(f"Successfully deleted city {city.name}", "success")
    return redirect(url_for('index_get'))


if __name__ == "__main__":
    app.run(debug = True)