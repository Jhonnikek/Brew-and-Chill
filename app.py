from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask (__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    product_name = db.Column(db.String(40),nullable = False)
    price = db.Column(db.Float, nullable = False)
    status = db.Column(db.String, nullable = False)
    description = db.Column(db.String(500), nullable = False)

    def __repr__(self):
        return f'<product {self.name}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    client_name = db.Column(db.String(25), nullable = False)
    last_name = db.Column(db.String(25), nullable = False)
    phone = db.Column(db.String, nullable = False)
    email = db.Column(db.String(120), nullable = False)

    def __repr__(self):
        return f'<client {self.client_name}>'
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  
    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False, default="cash")
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
    status = db.Column(db.String(20), nullable=False)
class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', backref=db.backref('details', lazy=True))
    product = db.relationship('Product')

@app.route('/')
def index():
    products_count = Product.query.count()
    clients_count = Client.query.count()
    orders_count = Order.query.count()
    order_details_count = OrderDetail.query.count()
    recent_orders = Order.query.order_by(Order.date.desc()).limit(5).all()
    return render_template('index.html', products_count=products_count, clients_count=clients_count, orders_count=orders_count, order_details_count=order_details_count, recent_orders=recent_orders)

@app.route('/products')
def show_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('products/products.html', products=products)

@app.route('/products/new', methods=['GET','POST'])
def create_product():
    if request.method == 'POST':
        product_name = request.form["product_name"]
        price = request.form["price"]
        status = request.form["status"]
        description = request.form["description"]
        
        new_product = Product (
            product_name=product_name, 
            price=price, status=status,
            description=description)
        
        db.session.add(new_product)
        
        db.session.commit()
        return redirect(url_for("show_products"))
    
    return render_template ("products/products_form.html", product=None)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.product_name = request.form["product_name"]
        product.price = request.form["price"]
        product.status = request.form["status"]
        product.description = request.form['description']
        
        db.session.commit()
        return redirect(url_for("show_products"))
    
    return render_template ("products/products_form.html", product=product)

@app.route('/products/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('show_products'))

@app.route('/clients')
def show_clients():
    clients = Client.query.order_by(Client.id.desc()).all()
    return render_template('clients/clients.html', clients=clients)

@app.route('/clients/new', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        client_name = request.form["client_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        
        new_client = Client (
            client_name=client_name,
            last_name=last_name,
            phone=phone,
            email=email)
        
        db.session.add(new_client)

        db.session.commit()
        return redirect(url_for("create_order"))
    
    return render_template ("clients/clients_form.html", client=None)

@app.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.client_name = request.form["client_name"]
        client.last_name = request.form["last_name"]
        client.phone = request.form["phone"]
        client.email = request.form["email"]

        db.session.commit()
        return redirect(url_for("show_clients"))

    return render_template ("clients/clients_form.html", client=client)

@app.route('/clients/delete/<int:id>')
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('show_clients'))

@app.route('/orders')
def show_orders():
    orders = Order.query.order_by(Order.date.desc()).all()
    return render_template('orders/orders.html', orders=orders)

@app.route('/orders/new', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        date_str = request.form["date"]
        date_value = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        client_id = request.form["client_id"] 
        status = request.form["status"]
        payment_method = request.form["payment_method"]
        total = 0
        
        new_order = Order(
            date=date_value,
            client_id=client_id,
            status=status,
            payment_method=payment_method,
            total=total)
        
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('create_order_detail', order_id=new_order.id))
    
    clients = Client.query.order_by(Client.client_name).all()
    return render_template("orders/orders_form.html", order=None, clients=clients)

@app.route('/orders/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        date_str = request.form["date"]
        order.date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        order.client_id = request.form["client_id"]
        order.status = request.form["status"]
        order.payment_method = request.form["payment_method"]
        order.total = request.form["total"]
        
        db.session.commit()
        return redirect(url_for("show_orders"))
    
    clients = Client.query.order_by(Client.client_name).all()
    return render_template("orders/orders_form.html", order=order, clients=clients)

@app.route('/orders/delete/<int:id>')
def delete_order(id):
    order = Order.query.get_or_404(id)
    OrderDetail.query.filter_by(order_id=id).delete()
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('show_orders'))

@app.route('/orders/<int:order_id>')
def show_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('orders/order_details.html', order=order)

@app.route('/orders/<int:order_id>/details/new', methods=["GET", "POST"])
def create_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    products = Product.query.order_by(Product.product_name).all()
    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity_str = request.form.get("quantity")

        if not product_id or not quantity_str:
            return "Missing product or quantity", 400

        quantity = int(quantity_str)
        product = Product.query.get_or_404(product_id)
        
        unit_price = product.price
        subtotal = quantity * unit_price
        
        new_detail = OrderDetail(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
        db.session.add(new_detail)

        order.total += subtotal
        db.session.commit()
        
        return redirect(url_for("show_order_details", order_id=order.id))

    return render_template("orders/order_detail_form.html", detail=None, order=order, products=products)

@app.route('/order_detail/edit/<int:id>', methods=['GET', 'POST'])
def edit_order_detail(id):
    detail = OrderDetail.query.get_or_404(id)
    order = detail.order
    products = Product.query.order_by(Product.product_name).all()

    if request.method == 'POST':

        original_subtotal = detail.subtotal

        detail.product_id = request.form["product_id"]
        detail.quantity = int(request.form["quantity"])

        product = Product.query.get_or_404(detail.product_id)
        detail.unit_price = product.price
        detail.subtotal = detail.quantity * detail.unit_price

        order.total = (order.total - original_subtotal) + detail.subtotal

        db.session.commit()
        return redirect(url_for("show_order_details", order_id=order.id))

    return render_template("orders/order_detail_form.html", detail=detail, order=order, products=products)

@app.route('/order_detail/delete/<int:id>')
def delete_order_detail(id):
    detail = OrderDetail.query.get_or_404(id)
    order = detail.order

    order.total -= detail.subtotal

    db.session.delete(detail)
    db.session.commit()
    
    return redirect(url_for("show_order_details", order_id=order.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
