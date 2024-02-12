from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)


API_Key = "TOP_SECRET"

# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Success message
success_message = {
    "response": {
        "success": "Successfully added the new cafe"
    }
}


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


def convert_cafe_to_dict(cafe):
    full_dict = {}
    id_dict = {
        "id": cafe.id
    }
    full_dict[cafe.id] = {
        "cafe": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price
    }
    return full_dict


def convert_to_dict(list):
    id_dict = {}
    full_dict = {}
    for i in list:
        id_dict = {
            "id": i.id
        }
        full_dict[i.id] = {
            "cafe": i.name,
            "map_url": i.map_url,
            "img_url": i.img_url,
            "location": i.location,
            "seats": i.seats,
            "has_toilet": i.has_toilet,
            "has_wifi": i.has_wifi,
            "has_sockets": i.has_sockets,
            "can_take_calls": i.can_take_calls,
            "coffee_price": i.coffee_price
        }
    return full_dict


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET", "POST"])
def random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars()
    cafe_list = all_cafes.all()
    random_choice = random.choice(cafe_list)
    return jsonify(convert_cafe_to_dict(random_choice))


@app.route("/all", methods=["GET", "POST"])
def all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes_list = result.scalars()
    cafe_list = all_cafes_list.all()
    # print(cafe_list)
    cafe_dict = convert_to_dict(cafe_list)
    print(cafe_dict)
    return jsonify(cafe_dict)


@app.route("/search", methods=["GET", "POST"])
def search_cafes():
    query = request.args.getlist('loc')
    print(query[0])
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query[0].title()))
    search_cafes_list = result.scalars()
    search_result = search_cafes_list.fetchall()
    print(search_result)
    print(len(search_result))
    if len(search_result) == 0:
        return f"No restaurants in {query[0]}"
    elif len(search_result) == 1:
        search_dict = convert_to_dict(search_result)
        return search_dict
    else:
        search_dict = convert_to_dict(search_result)
        return search_dict


# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_cafes():
    cafe_to_add = Cafe()
    cafe_to_add.name = request.args.getlist('name')[0]
    cafe_to_add.map_url = request.args.getlist('map_url')[0]
    cafe_to_add.img_url = request.args.getlist('img_url')[0]
    cafe_to_add.location = request.args.getlist('location')[0]
    cafe_to_add.seats = request.args.getlist('seats')[0]
    cafe_to_add.has_toilet = int(request.args.getlist('has_toilet')[0])
    cafe_to_add.has_wifi = int(request.args.getlist('has_wifi')[0])
    cafe_to_add.has_sockets = int(request.args.getlist('has_sockets')[0])
    cafe_to_add.can_take_calls = int(request.args.getlist('can_take_calls')[0])
    cafe_to_add.coffee_price = request.args.getlist('coffee_price')[0]
    with app.app_context():
        db.session.add(cafe_to_add)
        db.session.expire_on_commit = False
        db.session.commit()
    return jsonify(success_message)


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_cafe(cafe_id):
    result = db.get_or_404(ident=int(cafe_id), entity=Cafe)
    new_price = request.args.getlist('price')[0]
    if result.name == "None":
        return "Such a cafe does not exist"
    else:
        with app.app_context():
            cafe_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == int(cafe_id))).scalar()
            cafe_to_update.coffee_price = new_price
            db.session.commit()
        return f"new price updated to {new_price}"


# HTTP DELETE - Delete Record
@app.route("/delete-cafe/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    result = db.get_or_404(ident=int(cafe_id), entity=Cafe)
    if request.args.getlist('api-key')[0] == API_Key:
        with app.app_context():
            cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == int(cafe_id))).scalar()
            db.session.delete(cafe_to_delete)
            db.session.commit()
        return f"Cafe Deleted"
    else:
        return "Wrong API KEY"


if __name__ == '__main__':
    app.run(debug=True)
