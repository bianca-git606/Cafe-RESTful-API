from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # dictionary representation of the object
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    def str_to_bool(arg_from_url):
        if arg_from_url in ['True', 'true', 'T', 't', 'Yes', 'yes', 'y', '1']:
            return True
        else:
            return False
    


@app.route("/")
def home():
    return render_template("index.html")



@app.route('/random')
def random():
    # quickest way to query in case the database scales
    rows = Cafe.query.count()
    random_offset = random.randint(0, rows - 1)
    random_cafe = Cafe.query.offset(random_offset).first()
    return jsonify(random_cafe)

## HTTP GET - Read Record

@app.route('/all')
def cafes():
    # try to query the cafe in case the database is empty
    try:
        cafes = Cafe.query.all()
        if cafes:
            return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    except OperationalError:
        return jsonify(error={"Empty database": "Sorry we currently have no data to show."})
    

@app.route('/search')
def get_cafe_at_location():
    # get the param
    query_location = request.args.get("loc")
    # search for the cafe with that location
    cafe = Cafe.query.filter_by(location=query_location).first()
    # check if it exists
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "There are no cafes in that location in our database."})


## HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add_a_cafe():

    # associate the params to create a new Cafe object 
    new_cafe = Cafe(name=request.args.get("name"),
                    map_url=request.args.get("map_url"),
                    img_url=request.args.get("img_url"),
                    location=request.args.get("location"),
                    seats=request.args.get("seats"),
                    has_toilet=Cafe.str_to_bool(request.args.get("has_toilet")),
                    has_wifi=Cafe.str_to_bool(request.args.get("has_wifi")),
                    has_sockets=Cafe.str_to_bool(request.args.get("has_sockets")),
                    can_take_calls=Cafe.str_to_bool(request.args.get("can_take_calls")),
                    coffee_price=request.args.get("coffee_price")
                    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe"})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=['PATCH'])
def update_price(id):

    new_price = request.args.get("new_price")
    cafe = Cafe.query.get(id)
    # check if the id points to an object in the database
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not found": "Cannot find a cafe with that id"})


## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:id>', methods=['DELETE'])
def delete_a_cafe(id):
    # set an api_key
    api_key = "secretsecretkey"
    # get the cafe the client wants to delete
    cafe = cafe = db.session.query(Cafe).get(id)
    # get the api_key from the browser
    user_api_key = request.args.get("api-key")
    # check if key is valid
    if user_api_key == api_key:
        if cafe: 
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "The cafe was successfully deleted from the database"}), 200
        
        return jsonify(error={"Not Found": "Sorry, we could not find a cafe with that id."}), 404
    return jsonify(error={"Permission Denied": "Wrong api-key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
