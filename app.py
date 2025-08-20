from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

# -------- Models --------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    description = db.Column(db.Text)

# -------- Routes --------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description} for p in products])
    if request.method == 'POST':
        data = request.get_json()
        p = Product(name=data['name'], price=data['price'], description=data['description'])
        db.session.add(p)
        db.session.commit()
        return jsonify({'id': p.id, 'name': p.name}), 201

@app.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
def api_product_detail(id):
    p = Product.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.get_json()
        p.name = data.get('name', p.name)
        p.price = data.get('price', p.price)
        p.description = data.get('description', p.description)
        db.session.commit()
        return jsonify({'id': p.id, 'name': p.name})
    elif request.method == 'DELETE':
        db.session.delete(p)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed = generate_password_hash(data['password'])
    u = User(username=data['username'], password=hashed)
    db.session.add(u); db.session.commit()
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    u = User.query.filter_by(username=data['username']).first()
    if u and check_password_hash(u.password, data['password']):
        session['user_id'] = u.id
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/api/cart')
def api_cart():
    product_ids = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add sample products
        if Product.query.count() == 0:
            sample_products = [
                Product(name='Smartphone', price=699.99, description='Latest Android smartphone with high-end specs'),
                Product(name='Laptop', price=1299.99, description='Lightweight laptop perfect for work and play'),
                Product(name='Wireless Headphones', price=199.99, description='Noise-cancelling, long battery life'),
                Product(name='Gaming Mouse', price=59.99, description='RGB, high DPI, ultra-responsive'),
                Product(name='4K Monitor', price=349.99, description='Ultra HD monitor for work and gaming')
            ]
            db.session.add_all(sample_products)
            db.session.commit()
            print("Sample products added.")

    app.run(debug=True)

