from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Se\xb1z\x9bD_\xdc\xd3\xc2|\x7f|\xf0\x83Yw\xe2\xf7%=\xf0\xe5'
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
    is_active = BooleanField('Is Active')
    manufacturer = SelectField('Manufacturer', coerce=int, validators=[DataRequired()])


class CarForm(FlaskForm):
    color = StringField('Color')
    horsepower = IntegerField('Horsepower')
    consumption = IntegerField('Consumption')
    manufacture_date = StringField('Manufacture Date')
    is_drivable = BooleanField('Is Drivable')
    car_model = SelectField('Car Model', coerce=int, validators=[DataRequired()])


class CarFilterForm(FlaskForm):
    manufacturer = SelectField('Manufacturer', coerce=int)
    car_model = SelectField('Car Model', coerce=int)

    def __init__(self, *args, **kwargs):
        super(CarFilterForm, self).__init__(*args, **kwargs)
        self.manufacturer.choices = [(manufacturer.id, manufacturer.name) for manufacturer in Manufacturer.query.all()]
        self.car_model.choices = [(car_model.id, car_model.name) for car_model in CarModel.query.all()]


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
        if manufacturer:
            db.session.delete(manufacturer)
            db.session.commit()
            flash('Manufacturer deleted successfully', 'success')
        else:
            flash('Manufacturer not found', 'danger')
        return redirect(url_for('index'))
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
from sqlalchemy import or_, and_


@app.route('/', methods=['GET', 'POST'])
def index():
    manufacturers = Manufacturer.query.all()
    car_models = CarModel.query.all()
    cars = Car.query.all()

    form = CarFilterForm()

    if form.validate_on_submit():
        manufacturer_id = form.manufacturer.data
        car_model_id = form.car_model.data

        if manufacturer_id and car_model_id:
            cars = Car.query.join(CarModel).filter(
                and_(Car.model_id == car_model_id, CarModel.manufacturer_id == manufacturer_id)
            ).all()
        elif manufacturer_id:
            cars = Car.query.join(CarModel).filter(
                CarModel.manufacturer_id == manufacturer_id
            ).all()
        elif car_model_id:
            cars = Car.query.filter_by(model_id=car_model_id).all()
        else:
            cars = Car.query.all()

    return render_template('index.html', manufacturers=manufacturers,
                           car_models=car_models, cars=cars, form=form)


# Přidání/úprava výrobce
@app.route('/add_manufacturer', methods=['GET', 'POST'])
def add_manufacturer():
    form = ManufacturerForm()
    if form.validate_on_submit():
        manufacturer = Manufacturer(name=form.name.data,
                                    street=form.street.data,
                                    city=form.city.data,
                                    zip_code=form.zip_code.data,
                                    country=form.country.data)
        db.session.add(manufacturer)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_manufacturer.html', form=form)


# Přidání/úprava modelu auta
@app.route('/add_model', methods=['GET', 'POST'])
def add_model():
    form = CarModelForm()

    manufacturers = Manufacturer.query.all()  # Získání seznamu výrobců pro formulář
    # Nastavení výběru výrobce:
    form.manufacturer.choices = [(manufacturer.id, manufacturer.name) for manufacturer in manufacturers]

    if form.validate_on_submit():
        car_model = CarModel(manufacturer_id=form.manufacturer.data,  # Přiřazení id výrobce
                             name=form.name.data,
                             category=form.category.data,
                             price_range=form.price_range.data,
                             release_year=form.release_year.data,
                             is_active=form.is_active.data)
        db.session.add(car_model)
        db.session.commit()
        return redirect(url_for('index'))
    # Předání seznamu výrobců do šablony
    return render_template('add_model.html', form=form, manufacturers=manufacturers)


# Přidání/úprava automobilu
@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    form = CarForm()

    car_models = CarModel.query.all()
    form.car_model.choices = [(car_model.id, car_model.name) for car_model in car_models]

    if form.validate_on_submit():
        car = Car(model_id=form.car_model.data,
                  color=form.color.data,
                  horsepower=form.horsepower.data,
                  consumption=form.consumption.data,
                  manufacture_date=form.manufacture_date.data,
                  is_drivable=form.is_drivable.data)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_car.html', form=form, car_models=car_models)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
