# app.py (Final Deployment Version)
from flask import Flask, render_template, redirect, url_for, flash, request, make_response, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import csv
import io
import os
from sqlalchemy import func
from datetime import date, timedelta
from flask_migrate import Migrate # NEW IMPORT

from models import db, User, InventoryItem, Sale
from forms import LoginForm, RegistrationForm, InventoryForm, SaleForm

app = Flask(__name__)

# --- Configuration ---
# This setup works for both local development and Render deployment.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_default_secret_key_for_local_dev')
# Use the cloud database URL if available, otherwise use a local SQLite file.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'site.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
db.init_app(app)
migrate = Migrate(app, db) # NEW: INITIALIZE FLASK-MIGRATE
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# REMOVED: The with app.app_context() block is no longer needed.
# The build.sh script will now handle database creation.

@app.context_processor
def inject_low_stock_alert():
    if current_user.is_authenticated:
        low_stock_items = InventoryItem.query.filter_by(owner=current_user).filter(InventoryItem.quantity <= InventoryItem.low_stock_threshold).all()
        return dict(low_stock_items=low_stock_items)
    return dict(low_stock_items=[])

# --- All routes below this line remain exactly the same ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('That username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# (All other routes - login, logout, dashboard, inventory, sales, etc. - are unchanged)
# ...
# ... (rest of the file is the same)
# ...
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    inventory_count = InventoryItem.query.filter_by(owner=current_user).count()
    sales_count = Sale.query.filter_by(seller=current_user).count()
    total_revenue = db.session.query(func.sum(Sale.total_price)).filter_by(seller=current_user).scalar() or 0.0
    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    date_labels = [(seven_days_ago + timedelta(days=i)).strftime("%A") for i in range(7)]
    sales_by_day = db.session.query(func.date(Sale.date_sold), func.sum(Sale.total_price)).filter_by(seller=current_user).filter(func.date(Sale.date_sold) >= seven_days_ago).group_by(func.date(Sale.date_sold)).all()
    sales_dict = {str(d): s for d, s in sales_by_day}
    sales_data = [sales_dict.get(str(seven_days_ago + timedelta(days=i)), 0) for i in range(7)]
    return render_template('dashboard.html', inventory_count=inventory_count, sales_count=sales_count, total_revenue=total_revenue, sales_chart_labels=date_labels, sales_chart_data=sales_data)

@app.route('/inventory')
@login_required
def inventory():
    page = request.args.get('page', 1, type=int)
    items = InventoryItem.query.filter_by(owner=current_user).order_by(InventoryItem.date_added.desc()).paginate(page=page, per_page=10)
    return render_template('inventory.html', items=items)

@app.route('/add_inventory', methods=['GET', 'POST'])
@login_required
def add_inventory():
    form = InventoryForm()
    if form.validate_on_submit():
        item = InventoryItem(name=form.name.data, quantity=form.quantity.data, price=form.price.data, low_stock_threshold=form.low_stock_threshold.data, owner=current_user)
        db.session.add(item)
        db.session.commit()
        flash('Inventory item added successfully!', 'success')
        return redirect(url_for('inventory'))
    return render_template('add_inventory.html', form=form)

@app.route('/edit_inventory/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    form = InventoryForm()
    if form.validate_on_submit():
        item.name = form.name.data
        item.quantity = form.quantity.data
        item.price = form.price.data
        item.low_stock_threshold = form.low_stock_threshold.data
        db.session.commit()
        flash('Item has been updated successfully!', 'success')
        return redirect(url_for('inventory'))
    elif request.method == 'GET':
        form.name.data = item.name
        form.quantity.data = item.quantity
        form.price.data = item.price
        form.low_stock_threshold.data = item.low_stock_threshold
    return render_template('edit_inventory.html', form=form, item=item)

@app.route('/delete_inventory/<int:item_id>')
@login_required
def delete_inventory(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Inventory item deleted!', 'success')
    return redirect(url_for('inventory'))

@app.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    sale_records = Sale.query.filter_by(seller=current_user).order_by(Sale.date_sold.desc()).paginate(page=page, per_page=10)
    return render_template('sales.html', sale_records=sale_records)

@app.route('/add_sale', methods=['GET', 'POST'])
@login_required
def add_sale():
    form = SaleForm()
    inventory_items = InventoryItem.query.filter_by(owner=current_user).all()
    if form.validate_on_submit():
        item_sold = InventoryItem.query.filter_by(name=form.product_name.data, owner=current_user).first()
        if not item_sold:
            flash(f'Product "{form.product_name.data}" not found in your inventory.', 'danger')
            return redirect(url_for('add_sale'))
        if item_sold.quantity < form.quantity.data:
            flash(f'Not enough stock for "{item_sold.name}". Only {item_sold.quantity} available.', 'warning')
            return redirect(url_for('add_sale'))
        sale = Sale(product_name=form.product_name.data, quantity=form.quantity.data, total_price=form.total_price.data, seller=current_user)
        item_sold.quantity -= form.quantity.data
        db.session.add(sale)
        db.session.commit()
        flash('Sale recorded and inventory updated successfully!', 'success')
        return redirect(url_for('sales'))
    return render_template('add_sale.html', form=form, items=inventory_items)

@app.route('/charts')
@login_required
def charts():
    inventory = InventoryItem.query.filter_by(owner=current_user).all()
    inventory_labels = [item.name for item in inventory]
    inventory_values = [item.quantity for item in inventory]
    sales_data = db.session.query(Sale.product_name, func.sum(Sale.quantity)).filter_by(seller=current_user).group_by(Sale.product_name).all()
    sales_labels = [data[0] for data in sales_data]
    sales_values = [data[1] for data in sales_data]
    return render_template('charts.html', inventory_labels=inventory_labels, inventory_values=inventory_values, sales_labels=sales_labels, sales_values=sales_values)

@app.route('/export/inventory')
@login_required
def export_inventory():
    items = InventoryItem.query.filter_by(owner=current_user).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Quantity', 'Price', 'Date Added', 'Low Stock Threshold'])
    for item in items:
        writer.writerow([item.id, item.name, item.quantity, item.price, item.date_added.strftime('%Y-%m-%d'), item.low_stock_threshold])
    csv_data = output.getvalue()
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=inventory_export.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/export/sales')
@login_required
def export_sales():
    sales = Sale.query.filter_by(seller=current_user).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Product Name', 'Quantity Sold', 'Total Price', 'Date of Sale'])
    for sale in sales:
        writer.writerow([sale.id, sale.product_name, sale.quantity, sale.total_price, sale.date_sold.strftime('%Y-%m-%d %H:%M:%S')])
    csv_data = output.getvalue()
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=sales_export.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

# No __main__ block is needed for Gunicorn deployment