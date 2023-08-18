from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/carsdb'
db = SQLAlchemy(app)
api = Api(app)


# Definice databázových modelů
class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100))
    city = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    country = db.Column(db.String(50))


class CarModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price_range = db.Column(db.String(50))
    release_year = db.Column(db.Integer)
    is_active = db.Column(db.Boolean)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('car_model.id'), nullable=False)
    color = db.Column(db.String(50))
    horsepower = db.Column(db.Integer)
    consumption = db.Column(db.Float)
    manufacture_date = db.Column(db.Date)
    is_drivable = db.Column(db.Boolean)


# Formuláře pro přidání/editaci dat
class ManufacturerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    street = StringField('Street')
    city = StringField('City')
    zip_code = StringField('ZIP Code')
    country = StringField('Country')


class CarModelForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = StringField('Category')
    price_range = StringField('Price Range')
    release_year = IntegerField('Release Year')
    is_active = SelectField('Is Active', choices=[(True, 'Yes'), (False, 'No')])


class CarForm(FlaskForm):
    color = StringField('Color')
    horsepower = IntegerField('Horsepower')
    consumption = IntegerField('Consumption')
    manufacture_date = StringField('Manufacture Date')
    is_drivable = SelectField('Is Drivable', choices=[(True, 'Yes'), (False, 'No')])


# API Resources
class ManufacturerResource(Resource):
    def get(self, manufacturer_id):
        manufacturer = Manufacturer.query.get(manufacturer_id)
        # Kód pro získání dat

    def put(self, manufacturer_id):
        manufacturer = Manufacturer.query.get(manufacturer_id)
        # Kód pro aktualizaci dat

    def delete(self, manufacturer_id):
        manufacturer = Manufacturer.query.get(manufacturer_id)
        # Kód pro smazání dat


class CarModelResource(Resource):
    def get(self, model_id):
        car_model = CarModel.query.get(model_id)
        # Kód pro získání dat

    def put(self, model_id):
        car_model = CarModel.query.get(model_id)
        # Kód pro aktualizaci dat

    def delete(self, model_id):
        car_model = CarModel.query.get(model_id)
        # Kód pro smazání dat


class CarResource(Resource):
    def get(self, car_id):
        car = Car.query.get(car_id)
        # Kód pro získání dat

    def put(self, car_id):
        car = Car.query.get(car_id)
        # Kód pro aktualizaci dat

    def delete(self, car_id):
        car = Car.query.get(car_id)
        # Kód pro smazání dat


# Přiřazení URL ke zdrojům API
api.add_resource(ManufacturerResource, '/api/manufacturer/<int:manufacturer_id>')
api.add_resource(CarModelResource, '/api/model/<int:model_id>')
api.add_resource(CarResource, '/api/car/<int:car_id>')


# Hlavní stránka pro zobrazení dat
@app.route('/')
def index():
    manufacturers = Manufacturer.query.all()
    car_models = CarModel.query.all()
    cars = Car.query.all()
    return render_template('index.html', manufacturers=manufacturers,
                           car_models=car_models, cars=cars)


# Přidání/úprava výrobce
@app.route('/add_manufacturer', methods=['GET', 'POST'])
def add_manufacturer():
    form = ManufacturerForm()
    if form.validate_on_submit():
        manufacturer = Manufacturer(name=form.name.data, street=form.street.data, city=form.city.data,
                                    zip_code=form.zip_code.data, country=form.country.data)
        db.session.add(manufacturer)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_manufacturer.html', form=form)


# Přidání/úprava modelu auta
@app.route('/add_model', methods=['GET', 'POST'])
def add_model():
    form = CarModelForm()
    if form.validate_on_submit():
        car_model = CarModel(name=form.name.data, category=form.category.data, price_range=form.price_range.data,
                             release_year=form.release_year.data, is_active=form.is_active.data)
        db.session.add(car_model)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_model.html', form=form)


# Přidání/úprava automobilu
@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    form = CarForm()
    if form.validate_on_submit():
        car = Car(color=form.color.data, horsepower=form.horsepower.data, consumption=form.consumption.data,
                  manufacture_date=form.manufacture_date.data, is_drivable=form.is_drivable.data)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_car.html', form=form)


#    def add_cars():
#        manufacturers = Manufacturer.query.all()
#        car_models = CarModel.query.all()
#
#        if request.method == 'POST':
#            manufacturer_id = int(request.form.get('manufacturer'))
#            model_id = int(request.form.get('model'))
#
#            manufacturer = Manufacturer.query.get(manufacturer_id)
#            car_model = CarModel.query.get(model_id)
#
#            if not manufacturer or not car_model:
#                flash('Invalid manufacturer or car model selected.', 'error')
#            else:
#                file = request.files['car_data']
#                if file and file.filename.endswith('.json'):
#                    try:
#                        cars_data = json.load(file)
#                        for car_data in cars_data:
#                            car = Car(model_id=model_id, color=car_data['color'], horsepower=car_data['horsepower'],
#                                      consumption=car_data['consumption'],
#                                      manufacture_date=car_data['manufacture_date'],
#                                      is_drivable=car_data['is_drivable'])
#                            db.session.add(car)
#                        db.session.commit()
#                        return redirect(url_for('index'))
#                    except json.JSONDecodeError:
#                        flash('Invalid JSON file format.', 'error')
#                else:
#                    flash('Please upload a valid JSON file.', 'error')
#
#        return render_template('add_cars.html', manufacturers=manufacturers, car_models=car_models)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
