from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, URLField
from wtforms.validators import InputRequired
import random
import os
import dotenv

new_file = dotenv.find_dotenv()
dotenv.load_dotenv(new_file)

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
dev_api_key = os.environ.get("API_KEY")
Bootstrap(app)
db = SQLAlchemy(app)


# WTF Form Configuration
class AddCafeForm(FlaskForm):
    """Creates and handles the form where you can input the name and map URL of your newly discovered cafe."""
    name = StringField(label="Name of Cafe", validators=[InputRequired()])
    map_url = URLField(label="Google Map URL Link", validators=[InputRequired()])
    img_url = URLField(label="Image URL Link", validators=[InputRequired()])
    location = StringField(label="Location", validators=[InputRequired()])
    seats = StringField(label="Number of Seats", validators=[InputRequired()])
    has_toilet = BooleanField(label="Has toilet")
    has_wifi = BooleanField(label="Has Wi-Fi")
    has_sockets = BooleanField(label="Has sockets")
    can_take_calls = BooleanField(label="Can take calls")
    coffee_price = StringField(label="Coffee Price", validators=[InputRequired()])
    submit = SubmitField(label="Add Cafe")


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(700), nullable=False)
    img_url = db.Column(db.String(700), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        """This line is a representation of each object(instance) when created in the database."""
        return '<Cafe %r>' % self.name


number_of_cafes = 0


with app.app_context():
    db.create_all()

    @app.route("/")
    def home():
        return render_template("index.html")

    # HTTP GET - Read Record
    @app.route("/random", methods=["GET"])
    def random_cafe():
        """Fetch a random Cafe record from the database in JSON format using SQLAlchemy"""
        cafes = db.session.query(Cafe).all()
        if request.method == "GET":
            rand_cafe = random.choice(cafes)
            # return {"cafe": jsonify(name=cafe.name, map=cafe.map_url, poster=cafe.img_url, location=cafe.location, sockets=cafe.has_sockets, lavatories=cafe.has_toilet, wifi=cafe.has_wifi, phone_calls=cafe.can_take_calls, seat_capacity=cafe.seats, coffee_price=cafe.coffee_price).json}
            return jsonify(cafe={
                "cafe name": rand_cafe.name,
                "map": rand_cafe.map_url,
                "poster": rand_cafe.img_url,
                "location": rand_cafe.location,
                "services": {
                    "sockets": rand_cafe.has_sockets,
                    "lavtories": rand_cafe.has_toilet,
                    "Wi-Fi": rand_cafe.has_wifi,
                    "phone-calls": rand_cafe.can_take_calls,
                    "seat-capacity": rand_cafe.seats,
                    "coffee-price": rand_cafe.coffee_price,
                },
            })

    @app.route("/all", methods=["GET"])
    def all_cafes():
        """Displays all records in the Cafe database in JSON format"""
        if request.method == "GET":
            cafes = db.session.query(Cafe).all()
            return jsonify(cafes=[{
                "cafe": {
                    "id": cafe.id,
                    "cafe name": cafe.name,
                    "map": cafe.map_url,
                    "poster": cafe.img_url,
                    "location": cafe.location,
                    "services": {
                        "sockets": cafe.has_sockets,
                        "lavtories": cafe.has_toilet,
                        "Wi-Fi": cafe.has_wifi,
                        "phone-calls": cafe.can_take_calls,
                        "seat-capacity": cafe.seats,
                        "coffee-price": cafe.coffee_price,
                    }
                }
            } for cafe in cafes])

    @app.route("/search", methods=["GET"])
    def search_location():
        args = request.args
        location = args.get("loc")
        cafes = Cafe.query.filter_by(location=location).all()
        if cafes:
            return jsonify(cafes=[{
                "cafe": {
                    "cafe name": cafe.name,
                    "map": cafe.map_url,
                    "poster": cafe.img_url,
                    "location": cafe.location,
                    "services": {
                        "sockets": cafe.has_sockets,
                        "lavtories": cafe.has_toilet,
                        "Wi-Fi": cafe.has_wifi,
                        "phone-calls": cafe.can_take_calls,
                        "seat-capacity": cafe.seats,
                        "coffee-price": cafe.coffee_price,
                    }
                }
            } for cafe in cafes])
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

    # HTTP POST - Create Record
    @app.route("/add", methods=["GET", "POST"])
    def add_cafe():
        new_cafe = AddCafeForm()
        if request.method == "POST" or new_cafe.validate_on_submit():
            cafe_to_add = Cafe(
                name=request.form.get("name"),
                map_url=request.form.get("map_url"),
                img_url=request.form.get("img_url"),
                location=request.form.get("location"),
                seats=request.form.get("seats"),
                has_toilet=bool(request.form.get("has_toilet")),
                has_wifi=bool(request.form.get("has_wifi")),
                has_sockets=bool(request.form.get("has_sockets")),
                can_take_calls=bool(request.form.get("can_take_calls")),
                coffee_price=request.form.get("coffee_price")
            )
            db.session.add(cafe_to_add)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."})
        else:
            return render_template("add_cafe.html", new=new_cafe)

    # HTTP PUT/PATCH - Update Record
    @app.route("/update-price/<cafe_id>", methods=["GET", "POST"])
    def update_price(cafe_id):
        cafe_to_edit = Cafe.query.get(int(cafe_id))
        if cafe_to_edit is None:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
        else:
            args = request.args
            print(cafe_to_edit.coffee_price)
            cafe_to_edit.coffee_price = args.get("new_price")
            print(cafe_to_edit.coffee_price)
            db.session.commit()
            return jsonify(response={"success": f"Successfully updated coffee price for {cafe_to_edit.name}"}), 200

    ## HTTP DELETE - Delete Record
    @app.route("/report-closed/<cafe_id>", methods=["GET", "POST"])
    def delete_cafe(cafe_id):
        args = request.args
        user_api_key = args.get("api-key")
        if user_api_key == dev_api_key:
            cafe_to_delete = Cafe.query.get(int(cafe_id))
            if cafe_to_delete is None:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404
            else:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(response={"success": f"So sad that {cafe_to_delete.name} is permanently closed."}), 200
        else:
            return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct API key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
