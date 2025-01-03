from django import db
from flask import Flask, jsonify,g, render_template, request, redirect, url_for, session,flash
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import random
import logging
from pymongo import MongoClient

from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/bookStore'
bcrypt = Bcrypt()

mongo = PyMongo(app)
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.bookStore
users = db.users
books_collection = db.books
login_manager = LoginManager()
login_manager.init_app(app)
ADMIN_USERNAME = 'haji_sha46'

def is_user_admin(username):
    return username == ADMIN_USERNAME

class User:
    def __init__(self, id, username, password, role=None):  # Add role with a default value
        self.id = id
        self.username = username
        self.password = password
        self.role = role  # Include the role if it's part of your requirements
        self.is_admin = is_user_admin(username)

    @property
    def is_authenticated(self):
        return True  # Assuming the user is authenticated after login

    @property
    def is_active(self):
        return True  # Assuming the user is active; you can add your logic here

    @property
    def is_anonymous(self):
        return False  # This should return True for anonymous users

    def get_id(self):
        return str(self.id) 
    
    @classmethod
    def get_by_username(cls, username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return cls(user_data['username'], user_data['password'])
        return None

  
@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data['_id']), user_data['username'], user_data['password'], user_data.get('role', 'User'))
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            print(f"Attempting to login with username: {username}")

            user_data = mongo.db.users.find_one({"username": username})
            print(f"Fetched user data: {user_data}")

            if user_data and check_password_hash(user_data['password'], password):
                print("Password match!")
                user = User(str(user_data['_id']), user_data['username'], user_data['password'], user_data.get('role', 'User'))  # Adjust based on User class
                login_user(user)
                session['user_id'] = str(user.id)
                # session['is_admin'] = user_data['username'] == ADMIN_USERNAME 
                print("Login successful! Welcome!")
                return redirect(url_for('index'))
            else:
                print("Invalid username or password.")
                flash('Invalid username or password.', 'danger')

        except Exception as e:
            print(f"Error during login process: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html')



@app.route('/')
def index():    
    books = list(mongo.db.books.find())
    random_books = random.sample(books, min(len(books), 35))  # Limit to 35 items
    username = current_user.username if current_user.is_authenticated else None
    is_admin = is_user_admin(username) if username else False  # Check if the user is an admin

    return render_template('index.html', 
                           logged_in=current_user.is_authenticated, 
                           books=random_books, 
                           current_user=current_user,
                           is_admin=is_admin)

@app.route('/home')
def home():
    if 'user_id' in session:
        books = list(books_collection.find())
        return render_template('home.html', books=books)
    return redirect(url_for('login'))

def valid_user(username, password):
    user = mongo.db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):  # Check if the password is correct
        session['user_id'] = str(user['_id'])  # Store user ID in session
        return True
    return False 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'customer') 
        # Check if email already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        # Insert the user into the database
        mongo.db.users.insert_one({
            'name': name,
            'email': email,
            'username': username,
            'password': password,
            'role': role
        })
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


orders_collection = db["orders"]

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for("index"))

    # Fetch books and orders
    books = list(books_collection.find())
    orders = list(orders_collection.find())

    # Enrich orders with book details
    enriched_orders = []
    for order in orders:
        if "items" in order and isinstance(order["items"], list):
            for item in order["items"]:
                book = books_collection.find_one({"isbn": item.get("isbn")})
                if book:
                    enriched_order = {
                        "order_id": str(order["_id"]),
                        "customer_name": order.get("user_id", "Unknown User"),
                        "book_title": item.get("title", "Unknown Title"),
                        "quantity": item.get("quantity", 0),
                        "total_price": order.get("total_price", 0),
                        "status": order.get("status", "pending"),  # Include status
                    }
                    enriched_orders.append(enriched_order)

    return render_template("admin.html", username=current_user.username, books=books, orders=enriched_orders)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Code to add the book to the database
        # Ensure you are retrieving data from the form correctly
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        # Add more fields as necessary

        # Example of inserting into MongoDB
        mongo.db.books.insert_one({
            'title': title,
            'author': author,
            'isbn': isbn,
            # Add more fields as necessary
        })
        return redirect(url_for('admin_dashboard'))  # Redirect after POST
    return render_template('add_book.html')  # Render the form for GET


@app.route('/edit_book/<isbn>', methods=['GET', 'POST'])
@login_required
def edit_book(isbn):
    book = books_collection.find_one({"isbn": isbn})
    
    if book is None:
        return "Book not found", 404

    success_message = None
    error_message = None

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        price = request.form.get('price')

        try:
            price = float(price)

            books_collection.update_one({"isbn": isbn}, {
                "$set": {
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "price": price
                }
            })
            success_message = "Book updated successfully!"
        except Exception as e:
            error_message = "An error occurred while updating the book. Please try again."

    return render_template("edit_book.html", book=book, success_message=success_message, error_message=error_message)


@app.route('/book/<isbn>')
def book_details(isbn):
    print(f"Searching for book with ISBN: {isbn}")  # Log the ISBN being searched
    book = mongo.db.books.find_one({'isbn': isbn})
    published_date = book.get('publishedDate', None)

    # Check if published_date is a datetime object or a string
    if isinstance(published_date, str):
        published_date = datetime.fromisoformat(published_date[:-1])  # Remove 'Z' and convert
    elif isinstance(published_date, dict) and '$date' in published_date:
        published_date = datetime.fromisoformat(published_date['$date'][:-1])  # Handle the dict format
    else:
        published_date = 'N/A'
    if not book:
        return "Book not found", 404
    
    page_count = book['pageCount']
    
    if 'pageCount' in book and book['pageCount'] > 0:
        price = round(book['pageCount'] * 2, 2) 
    else:
        price = round(random.randint(10, 20), 2)
        
    logged_in = 'user_id' in session  # Replace with your user session check
    return render_template('book_details.html', book=book, page_count=page_count, price=price, published_date=published_date,logged_in=logged_in)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    # Ensure user has a cart
    user_id = str(current_user.id)  # Change this line to use dot notation
    user = users.find_one({"_id": ObjectId(user_id)})

    if user and 'cart_details' in user:
        cart_items = user['cart_details']

        # Create a new order instance
        new_order = {
            'user_id': user_id,
            'items': cart_items,
            'total_price': sum(item['price'] for item in cart_items),
            'created_at': datetime.now()
        }

        # Insert the order into the database
        orders_collection.insert_one(new_order)

        # Clear the user's cart after placing the order
        users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'cart_details': []}}  # Clear the cart
        )

        return redirect(url_for('order_success'))
    else:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('view_cart'))
# class User(UserMixin, Document):
#     username = StringField(required=True, unique=True)
#     password = StringField(required=True)

#     @property
#     def id(self):
#         return str(self.pk)  # Use pk if using mongoengine
    

@app.route("/my_orders")
@login_required
def my_orders():
    # Fetch orders for the current user
    user_orders = list(orders_collection.find({"user_id": str(current_user.id)}))
    
    # Enrich orders with book details
    enriched_orders = []
    for order in user_orders:
        if "items" in order and isinstance(order["items"], list):
            for item in order["items"]:
                book = books_collection.find_one({"isbn": item.get("isbn")})
                enriched_order = {
                    "order_id": str(order["_id"]),
                    "book_title": item.get("title", "Unknown Title"),
                    "quantity": item.get("quantity", 0),
                    "total_price": order.get("total_price", 0),
                    "status": order.get("status", "pending"),  # Include status
                    "created_at": order.get("created_at")
                }
                enriched_orders.append(enriched_order)

    return render_template("my_orders.html", username=current_user.username, orders=enriched_orders)

@app.route("/view_orders")
@login_required
def view_orders():
    if not current_user.is_admin:
        return redirect(url_for("index"))

    # Fetch orders from the orders collection
    orders = list(orders_collection.find())
    
    # Enrich orders with book details
    enriched_orders = []
    for order in orders:
        if "items" in order and isinstance(order["items"], list):
            for item in order["items"]:
                book = books_collection.find_one({"isbn": item.get("isbn")})
                enriched_order = {
                    "order_id": str(order["_id"]),
                    "user_id": order.get("user_id", "Unknown User"),
                    "book_title": item.get("title", "Unknown Title"),
                    "quantity": item.get("quantity", 0),
                    "total_price": order.get("total_price", 0),
                    "status": order.get("status", "pending"),  # Include status
                    "created_at": order.get("created_at")
                }
                enriched_orders.append(enriched_order)

    return render_template("view_orders.html", username=current_user.username, orders=enriched_orders)


@app.route("/accept_order/<order_id>", methods=["POST"])
@login_required
def accept_order(order_id):
    if not current_user.is_admin:
        return redirect(url_for("index"))

    # Update the order status to 'accepted'
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "accepted"}}
    )
    
    if result.modified_count == 1:
        flash("Order accepted successfully!", "success")
    else:
        flash("Failed to accept order. Please try again.", "error")

    return redirect(url_for("admin_dashboard"))


@app.route('/order_success')
def order_success():
    return render_template('order_success.html', message="Your order has been placed successfully!")

@app.route('/delete_book/<string:isbn>', methods=['POST'])
def delete_book(isbn):
    print(f"Attempting to delete book with ISBN: {isbn}")  # Debug output
    # Try deleting by ISBN first
    delete_result = mongo.db.books.delete_one({"isbn": isbn})

    if delete_result.deleted_count == 0:
        # If no book was deleted by ISBN, try to delete by ID from the form
        book_id = request.form.get('id')  # Expecting the ID to be sent from the form
        if book_id:
            print(f"ISBN not found, trying to delete book with ID: {book_id}")  # Debug output
            mongo.db.books.delete_one({"_id": ObjectId(book_id)})

    return redirect(url_for('admin_dashboard'))


@app.route('/current_orders')
@login_required
def current_orders():
    orders = list(orders_collection.find())
    return render_template('current_orders.html', orders=orders)

@app.route('/filter_books', methods=['GET'])
def filter_books():
    selected_categories = request.args.getlist('categories')  # Get list of selected categories
    if selected_categories:
        # Fetch books that match the selected categories
        filtered_books = list(mongo.db.books.find({"categories": {"$in": selected_categories}}))
    else:
        # If no categories are selected, fetch all books
        filtered_books = list(mongo.db.books.find())
    
    return render_template('index.html', books=filtered_books)  # Render with the filtered books

@app.route('/cart')
@login_required
def cart():
    user_id = current_user.id
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    print(f"User data fetched: {user_data}")  # Debug print

    if user_data:
        cart_items = user_data.get('cart_details', [])
        print(f"Cart items: {cart_items}")  # Debug print
        return render_template('cart.html', cart_items=cart_items)

    return render_template('cart.html', cart_items=[])

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in.'}), 401

    # Get ISBN from JSON request
    isbn = request.json.get('isbn')  # Change this to the appropriate method based on how you're sending data
    book = fetch_book_by_isbn(isbn)

    if not book:
        return jsonify({'status': 'error', 'message': 'Book not found.'}), 404

    # Prepare the data to be stored
    cart_item = {
        'isbn': book.get('isbn'),
        'title': book.get('title'),
        'author': book.get('author', 'Unknown Author'),
        'price': book.get('price', 0),  # Ensure the price is correctly included
        'thumbnailUrl': book.get('thumbnailUrl', 'default_thumbnail.jpg'),  # Default if not available
        'quantity': 1  # Set initial quantity
    }

    # Update user cart in the database
    mongo.db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$addToSet': {'cart_details': cart_item}}
    )

    return jsonify({'status': 'success', 'message': 'Book added to cart!'})

    
def fetch_book_by_isbn(isbn):
    # Retrieve the book from the database
    book = mongo.db.books.find_one({'isbn': isbn})
    if not book:
        return None

    # Debugging: print the book data structure
    print(f"Fetched book data: {book}")

    # Ensure that you fetch the price correctly
    price = round(book.get('pageCount', 0) * 2, 2) if 'pageCount' in book and book['pageCount'] > 0 else round(random.uniform(10, 20), 2)

    return {
        'isbn': book['isbn'],
        'title': book.get('title', 'Unknown Title'),
        'author': book.get('author', 'Unknown Author'),  # Use .get() to avoid KeyError
        'price': price,  # Set the calculated price here
        'thumbnailUrl': book.get('thumbnailUrl', 'default_thumbnail.jpg'),  # Default thumbnail if not found
    }

    
@app.route('/cart')
@login_required
def view_cart():
    current_user_id = str(current_user.id)
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    cart_items = user.get('cart_details', [])  # Default to empty list if not found
    return render_template('cart.html', cart_items=cart_items)

@app.route('/remove_from_cart/<isbn>', methods=['POST'])
def remove_from_cart(isbn):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in.'}), 401

    # Remove the item from the user's cart in the database
    result = mongo.db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$pull': {'cart_details': {'isbn': isbn}}}  # Remove item matching the ISBN
    )

    if result.modified_count > 0:
        return jsonify({'status': 'success', 'message': 'Item removed from cart.'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found in cart.'}), 404


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

