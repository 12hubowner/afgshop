from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
import random
import hashlib

app = Flask(__name__)
app.secret_key = "afg_shop_secure_key_2026"
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def init_settings():
    settings = load_data(SETTINGS_FILE)
    if not settings:
        settings = {
            "store_name": "AFG Shop",
            "store_tagline": "Premium Streetwear",
            "currency_symbol": "$",
            "admin_password": "afgshop2026",
            "cashapp_tag": "$sabbotdiscord",
            "shipping_cost": 5.99,
            "free_shipping_over": 50.00
        }
        save_data(SETTINGS_FILE, settings)
    return settings

def init_products():
    products = load_data(PRODUCTS_FILE)
    if not products:
        products = {
            "hoodie_new": {
                "id": "hoodie_new",
                "name": "NEW STREET HOODIE",
                "price": 25.00,
                "category": "MEN",
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Black"],
                "images": ["https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/4281b5b83c05452ba4a82088be9a04bf~tplv-fhlh96nyum-crop-webp:800:800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"],
                "stock": 50,
                "description": "🔥 Premium oversized hoodie with 3D puff print design.",
                "badge": "BEST SELLER"
            },
            "hoodie_zip": {
                "id": "hoodie_zip",
                "name": "MEN'S FULL ZIP HOODIE",
                "price": 25.00,
                "category": "MEN",
                "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
                "colors": ["Black"],
                "images": ["https://p16-oec-general.ttcdn-us.com/tos-maliva-i-o3syd03w52-us/0f4afe60266e4ee1bf607d48bb26ae12~tplv-fhlh96nyum-crop-webp:1350:1800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"],
                "stock": 40,
                "description": "🔥 Versatile full zip hoodie jacket.",
                "badge": "NEW"
            },
            "hoodie_girl": {
                "id": "hoodie_girl",
                "name": "TWEEN GIRL CASUAL HOODIE",
                "price": 20.00,
                "category": "GIRLS",
                "sizes": ["3-4y", "4-5y", "5-6y", "7-8y", "9-10y", "11-12y"],
                "colors": ["Pink", "Black", "White"],
                "images": ["https://p16-oec-general.ttcdn-us.com/tos-maliva-i-o3syd03w52-us/ed919fe0498a4f30a6cb697a90ce4a89~tplv-fhlh96nyum-crop-webp:1350:1800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"],
                "stock": 35,
                "description": "🌸 Stylish fashion print hoodie for tween girls.",
                "badge": "TRENDING"
            },
            "hoodie_women": {
                "id": "hoodie_women",
                "name": "WOMEN'S CHERRY GRAPHIC",
                "price": 17.99,
                "category": "WOMEN",
                "sizes": ["S", "M", "L", "XL", "XXL", "XXXL"],
                "colors": ["Cherry Print"],
                "images": ["https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/83f2f21154d64373952da18efe38e9ed~tplv-fhlh96nyum-crop-webp:1600:1600.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"],
                "stock": 30,
                "description": "🍒 Stylish cherry graphic hoodie.",
                "badge": "SALE"
            }
        }
        save_data(PRODUCTS_FILE, products)
    return products

settings = init_settings()
products = init_products()

# ========== ROUTES ==========
@app.route('/')
def home():
    products = load_data(PRODUCTS_FILE)
    return render_template('index.html', products=products, settings=settings, user=session.get('user'))

@app.route('/shop')
def shop():
    products = load_data(PRODUCTS_FILE)
    category = request.args.get('category', 'ALL')
    if category != 'ALL':
        products = {k: v for k, v in products.items() if v['category'] == category}
    return render_template('shop.html', products=products, category=category, settings=settings, user=session.get('user'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    products = load_data(PRODUCTS_FILE)
    product = products.get(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('shop'))
    return render_template('product.html', product=product, product_id=product_id, settings=settings, user=session.get('user'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = load_data(PRODUCTS_FILE)
    cart_data = []
    total = 0
    for pid, qty in cart_items.items():
        if pid in products:
            product = products[pid]
            price = product['price']
            subtotal = price * qty
            total += subtotal
            cart_data.append({
                'id': pid,
                'name': product['name'],
                'price': price,
                'qty': qty,
                'image': product['images'][0] if product['images'] else '',
                'subtotal': subtotal
            })
    shipping = settings['shipping_cost'] if total < settings['free_shipping_over'] else 0
    grand_total = total + shipping
    return render_template('cart.html', cart=cart_data, total=total, shipping=shipping, grand_total=grand_total, settings=settings, user=session.get('user'))

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    qty = int(request.form.get('qty', 1))
    cart[product_id] = cart.get(product_id, 0) + qty
    session['cart'] = cart
    flash('✅ Item added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    session['cart'] = cart
    flash('🗑️ Item removed', 'info')
    return redirect(url_for('cart'))

@app.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', {})
    qty = int(request.form.get('qty', 0))
    if qty > 0:
        cart[product_id] = qty
    else:
        if product_id in cart:
            del cart[product_id]
    session['cart'] = cart
    flash('🔄 Cart updated', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'user' not in session:
        flash('Please login to checkout', 'warning')
        return redirect(url_for('login'))
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))
    return render_template('checkout.html', settings=settings, user=session.get('user'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        flash('Please login to place an order', 'warning')
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    cart_items = session.get('cart', {})
    products = load_data(PRODUCTS_FILE)
    
    items_list = []
    total = 0
    for pid, qty in cart_items.items():
        if pid in products:
            product = products[pid]
            price = product['price']
            subtotal = price * qty
            total += subtotal
            items_list.append({
                'id': pid,
                'name': product['name'],
                'price': price,
                'qty': qty,
                'subtotal': subtotal
            })
    
    shipping = settings['shipping_cost'] if total < settings['free_shipping_over'] else 0
    grand_total = total + shipping
    
    order_id = f"AFG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    order_data = {
        'order_id': order_id,
        'customer': name,
        'email': email,
        'phone': phone,
        'address': address,
        'items': items_list,
        'subtotal': total,
        'shipping': shipping,
        'total': grand_total,
        'status': 'Pending',
        'payment_status': 'Unpaid',
        'date': datetime.now().isoformat(),
        'cashapp_tag': settings.get('cashapp_tag', '$sabbotdiscord')
    }
    
    orders = load_data(ORDERS_FILE)
    orders[order_id] = order_data
    save_data(ORDERS_FILE, orders)
    
    # Add order to user
    users = load_data(USERS_FILE)
    if session['user'] in users:
        if 'orders' not in users[session['user']]:
            users[session['user']]['orders'] = []
        users[session['user']]['orders'].append(order_id)
        save_data(USERS_FILE, users)
    
    session['cart'] = {}
    
    flash(f'✅ Order placed! Order ID: {order_id}', 'success')
    return render_template('order_confirmation.html', order=order_data, settings=settings)

@app.route('/order_confirmation/<order_id>')
def order_confirmation(order_id):
    orders = load_data(ORDERS_FILE)
    order = orders.get(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('shop'))
    return render_template('order_confirmation.html', order=order, settings=settings, user=session.get('user'))

@app.route('/track_order', methods=['GET', 'POST'])
def track_order():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        orders = load_data(ORDERS_FILE)
        order = orders.get(order_id)
        if order:
            return render_template('track_order.html', order=order, found=True, settings=settings, user=session.get('user'))
        else:
            flash('Order not found.', 'error')
    return render_template('track_order.html', found=False, settings=settings, user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_data(USERS_FILE)
        if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['user'] = username
            session['user_data'] = users[username]
            flash('✅ Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            flash('❌ Invalid username or password', 'error')
    return render_template('login.html', settings=settings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_data(USERS_FILE)
        if username in users:
            flash('❌ Username already exists', 'error')
        else:
            users[username] = {
                'username': username,
                'email': email,
                'password': hashlib.sha256(password.encode()).hexdigest(),
                'created_at': datetime.now().isoformat(),
                'orders': []
            }
            save_data(USERS_FILE, users)
            flash('✅ Account created! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', settings=settings)

@app.route('/logout')
def logout():
    session.clear()
    flash('✅ Logged out', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('login'))
    
    user = session.get('user_data', {})
    orders = load_data(ORDERS_FILE)
    user_orders = []
    if user and 'orders' in user:
        for order_id in user['orders']:
            if order_id in orders:
                user_orders.append(orders[order_id])
    
    return render_template('profile.html', user=user, orders=user_orders, settings=settings)

# ========== ADMIN ROUTES ==========
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == settings['admin_password']:
            session['admin_logged_in'] = True
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password', 'error')
    return render_template('admin_login.html', settings=settings)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    products = load_data(PRODUCTS_FILE)
    orders = load_data(ORDERS_FILE)
    users = load_data(USERS_FILE)
    return render_template('admin_dashboard.html', products=products, orders=orders, users=users, settings=settings)

@app.route('/admin/add_product', methods=['GET', 'POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        product_id = request.form.get('id').lower().replace(' ', '_')
        products = load_data(PRODUCTS_FILE)
        if product_id in products:
            flash('Product ID exists!', 'error')
            return redirect(url_for('admin_add_product'))
        
        images = request.form.get('image_urls', '').split(',')
        images = [img.strip() for img in images if img.strip()]
        
        products[product_id] = {
            'id': product_id,
            'name': request.form.get('name'),
            'price': float(request.form.get('price')),
            'category': request.form.get('category'),
            'sizes': [s.strip() for s in request.form.get('sizes').split(',')],
            'colors': [c.strip() for c in request.form.get('colors').split(',')],
            'images': images if images else [],
            'stock': int(request.form.get('stock')),
            'description': request.form.get('description'),
            'badge': request.form.get('badge'),
            'rating': 4.5,
            'reviews': 0
        }
        save_data(PRODUCTS_FILE, products)
        flash('Product added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_product.html', settings=settings)

@app.route('/admin/delete_product/<product_id>')
def admin_delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    products = load_data(PRODUCTS_FILE)
    if product_id in products:
        del products[product_id]
        save_data(PRODUCTS_FILE, products)
        flash('Product deleted', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_order/<order_id>', methods=['POST'])
def admin_update_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    orders = load_data(ORDERS_FILE)
    if order_id in orders:
        orders[order_id]['status'] = request.form.get('status')
        orders[order_id]['payment_status'] = request.form.get('payment_status')
        save_data(ORDERS_FILE, orders)
        flash('Order updated', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        settings_data = load_data(SETTINGS_FILE)
        settings_data['store_name'] = request.form.get('store_name')
        settings_data['store_tagline'] = request.form.get('store_tagline')
        settings_data['currency_symbol'] = request.form.get('currency_symbol')
        settings_data['shipping_cost'] = float(request.form.get('shipping_cost', 5.99))
        settings_data['free_shipping_over'] = float(request.form.get('free_shipping_over', 50.00))
        settings_data['cashapp_tag'] = request.form.get('cashapp_tag')
        
        if request.form.get('admin_password'):
            settings_data['admin_password'] = request.form.get('admin_password')
        
        save_data(SETTINGS_FILE, settings_data)
        flash('Settings saved!', 'success')
        return redirect(url_for('admin_settings'))
    
    settings_data = load_data(SETTINGS_FILE)
    return render_template('admin_settings.html', settings=settings_data)

if __name__ == '__main__':
    print("=" * 50)
    print("🛍️ AFG SHOP")
    print("=" * 50)
    print("🔗 Website: http://0.0.0.0:5000")
    print("🔑 Admin Password: afgshop2026")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
