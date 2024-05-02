from flask import Flask, render_template, abort, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view




# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    
    return render_template('new_vendor.html')

@app.route('/consumer_home')
@login_required
def consumer_home():
    if current_user.is_authenticated and current_user.user_type == 'consumer':
        return render_template('consumer_home.html', user=current_user)
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))



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




if __name__ == '__main__':
    app.run(debug=True)
