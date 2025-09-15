#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found'}), 404)

    if request.method == 'GET':
        return make_response(jsonify(bakery.to_dict()), 200)

    # PATCH block: update only the fields provided in the form (we'll update name)
    if request.method == 'PATCH':
        new_name = request.form.get('name')
        if new_name:
            bakery.name = new_name

        db.session.commit()
        return make_response(jsonify(bakery.to_dict()), 200)
    
    # bakery = Bakery.query.filter_by(id=id).first()
    # bakery_serialized = bakery.to_dict()
    # return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

if __name__ == '__main__':
    app.run(port=5555, debug=True)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    if not name or price is None or bakery_id is None:
        return make_response(jsonify({'error': 'Missing required data'}), 400)

    try:
        price = float(price)
        bakery_id = int(bakery_id)
    except ValueError:
        return make_response(jsonify({'error': 'Invalid data type for price or bakery_id'}), 400)

    new_bg = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(new_bg)
    db.session.commit()

    return make_response(jsonify(new_bg.to_dict()), 201)


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return make_response(jsonify({'error': 'Baked good not found'}), 404)

    db.session.delete(bg)
    db.session.commit()

    return make_response(jsonify({'message': 'Baked good successfully deleted'}), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)