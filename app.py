from flask import Flask, render_template, abort, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, Vendor
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)

# Database configuration
# Encode special characters in your password
username = 'admin'
password = 'London@100'  # Example password with special character '@'
encoded_password = quote_plus(password)

# Construct the correct URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{username}:{encoded_password}@10.77.217.227/farmers_local_market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '\x98\x8ck\xcdpl}\x1f\x8f\x0e\x15\xd8\xdeC_\xff\xfd<r\xdb\x83\xc1\x08\x18'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user from the database
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and the password is correct
        if user and check_password_hash(user.password_hash, password):
            # Log the user in by setting the session variables
            login_user(user)  # Make sure you're using login_user when using Flask-Login
            flash('Login successful!', 'success')
            
            # Redirect to different pages based on user type
            if user.user_type == 'vendor':
                return redirect(url_for('vendor_home'))  # Redirect to the vendor-specific dashboard
            elif user.user_type == 'consumer':
                return redirect(url_for('consumer_home'))  # Redirect to the consumer-specific dashboard
            else:
                flash('Invalid user type.', 'error')
                return redirect(url_for('login'))  # Fallback in case of undefined user type
            
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form.get('user_type', 'consumer')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            flash('Username already exists. Please choose another one.', 'error')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user instance
        new_user = User(username=username, email=email, password_hash=hashed_password, user_type=user_type)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to the login page or home page after registration
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering user: {str(e)}', 'error')  # Show specific error to the developer
            print(f"Error: {str(e)}")  # Log to console for debugging
            return render_template('register.html', username=username, email=email, user_type=user_type)

    return render_template('register.html')


@app.route('/home')  # Ensure that only logged-in users can access this route
def home():
    if current_user.user_type == 'vendor':
        return render_template('vendor_home.html', user=current_user)
    elif current_user.user_type == 'consumer':
        return render_template('consumer_home.html', user=current_user)
    else:
        return redirect(url_for('error'))  # Handle cases where user_type might not be set correctly

@app.route('/new_vendor', methods=['GET', 'POST'])
@login_required
def new_vendor():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        
        # Assuming the Vendor model has a user_id field linking to the User model
        new_vendor = Vendor(
            user_id=current_user.id,  # Link the vendor to the currently logged-in user
            name=name,
            location=location,
            description=description
        )
        db.session.add(new_vendor)
        db.session.commit()
        flash('Your details have been successfully submitted!', 'success')
        return redirect(url_for('vendor_home'))  # Redirect to the vendor home page or another appropriate route

    return render_template('new_vendor.html')

@app.route('/consumer_home')
@login_required
def consumer_home():
    if current_user.is_authenticated and current_user.user_type == 'consumer':
        return render_template('consumer_home.html', user=current_user)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

@app.route('/vendor_home')
@login_required
def vendor_home():
    if current_user.is_authenticated and current_user.user_type == 'vendor':
        # Attempt to find the vendor associated with the current user
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        
        # Check if a vendor entry exists
        if vendor:
            products = Product.query.filter_by(vendor_id=vendor.id).all()
            return render_template('vendor_home.html', user=current_user, vendor=vendor, products=products, is_new_vendor=False)
        else:
            # No vendor found, treat as new vendor scenario or report it
            flash('No vendor profile found. Please create your vendor profile.', 'warning')
            return redirect(url_for('new_vendor'))  # Redirect to new vendor setup if no profile found
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))


# @app.route('/vendor_home')
# @login_required
# def vendor_home():
#     if current_user.is_authenticated and current_user.user_type == 'vendor':
#         vendor = Vendor.query.filter_by(user_id=current_user.id).first()
#         is_new_vendor = vendor is None  # True if no vendor details are found
#         print(vendor)
#         products = Product.query.filter_by(vendor_id=vendor.id).all()
#         print(products)
#         # Pass both 'vendor' and 'is_new_vendor' to the template for proper handling
#         return render_template('vendor_home.html', user=current_user, vendor=vendor, is_new_vendor=is_new_vendor)
#     else:
#         flash('Unauthorized access.', 'error')
#         return redirect(url_for('login'))

# @app.route('/vendor_home')
# @login_required
# def vendor_home():
#     if current_user.is_authenticated and current_user.user_type == 'vendor':
#         vendor = Vendor.query.filter_by(user_id=current_user.id).first()
#         print(vendor)
#         if vendor:
#             products = Product.query.filter_by(vendor_id=vendor.id).all()
#             print(products)  # Check if products are being fetched
#             is_new_vendor = False if products else True
#         else:
#             is_new_vendor = True  # No vendor details found

#         return render_template('vendor_home.html', user=current_user, vendor=vendor, is_new_vendor=is_new_vendor)
#     else:
#         flash('Unauthorized access.', 'error')
#         return redirect(url_for('login'))


@app.route('/edit_vendor/<int:vendor_id>', methods=['GET'])
@login_required
def edit_vendor(vendor_id):
    print("Vendor ID:", vendor_id)  # Debugging output
    vendor = Vendor.query.get_or_404(vendor_id)
    print("Vendor found:", vendor)  # More debugging output
    return render_template('edit_vendor.html', vendor=vendor)


    
@app.route('/update_vendor/<int:vendor_id>', methods=['POST'])
@login_required
def update_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.name = request.form['name']
    vendor.location = request.form['location']
    vendor.description = request.form['description']
    db.session.commit()
    flash('Vendor details updated successfully!', 'success')
    return redirect(url_for('vendor_home'))


@app.route('/add_product/<int:vendor_id>', methods=['GET', 'POST'])
@login_required
def add_product(vendor_id):
    if request.method == 'POST':
        # Ensure the current user is the vendor trying to add the product
        vendor = Vendor.query.get_or_404(vendor_id)
        if current_user.id != vendor.user_id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('vendor_home'))
        
        # Collect form data
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        availability = True if request.form.get('availability') == 'true' else False
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')

        # Create new product instance
        new_product = Product(
            vendor_id=vendor_id,
            name=name,
            description=description,
            price=price,
            availability=availability,
            contact_email=contact_email,
            contact_phone=contact_phone
        )

        # Add to the session and commit to the database
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('vendor_home'))  # Redirect to a vendor-specific dashboard or product list

    # GET request: show the add product form
    return render_template('add_product.html', vendor_id=vendor_id)

@app.route('/list_products/<int:vendor_id>')
@login_required
def list_products(vendor_id):
    products = Product.query.filter_by(vendor_id=vendor_id).all()
    return render_template('list_products.html', products=products, vendor_id=vendor_id)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.contact_email = request.form['contact_email']
        product.contact_phone = request.form['contact_phone']
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('vendor_home'))
    return render_template('edit_product.html', product=product)


# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/logout')
def logout():
    # Remove data from session, effectively logging the user out
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# @app.route('/markets')
# def markets():
#     return render_template('markets.html')

@app.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('product_detail.html', product=product)
    except Exception as e:
        abort(404)

# @app.route('/product_reviews/<int:product_id>')
# def product_reviews(product_id):
#     try:
#         product = Product.query.get_or_404(product_id)
#         return render_template('product_reviews.html', product=product)
#     except Exception as e:
#         abort(404)

@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/profile')
def profile():
    try:
        user = User.query.first()
        if user:
            return render_template('profile.html', user=user)
        else:
            return 'No user found', 404
    except Exception as e:
        abort(404)

# @app.route('/search_results')
# def search_results():
#     return render_template('search_results.html')

@app.route('/vendor_profile/<int:vendor_id>')
def vendor_profile(vendor_id):
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        return render_template('vendor_profile.html', vendor=vendor)
    except Exception as e:
        abort(404)

@app.route('/vendors')
def vendors():
    all_vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=all_vendors)

@app.route('/test_db')
def test_db():
    try:
        user = User.query.first()
        if user:
            return f'Success! Found user: {user.username}'
        else:
            return 'Connection successful but no users found.'
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
