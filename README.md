# Online Bookstore 🛒📚

Welcome to the **Online Bookstore** web application! This platform allows users to browse a wide variety of books, place orders, and track their purchases. For admins, the system provides the ability to manage book listings and orders seamlessly. Built using **Flask**, this application provides a clean and intuitive user experience with both front-end and back-end features.

---

## Features 🚀

### For **Users**:
- **Browse a Wide Collection**: Explore books across multiple genres.
- **Order Books**: Add books to your cart and proceed with secure checkout.
- **Track Orders**: View your previous orders and track their current status.
- **User Registration & Login**: Create your account to manage your orders and personal information.

### For **Admins**:
- **Manage Book Listings**: Add, edit, or remove books from the store.
- **Order Management**: View and manage customer orders, ensuring smooth processing.

---

## Tech Stack ⚙️

- **Frontend**: HTML, CSS, JavaScript (with custom styles and interactivity)
- **Backend**: Python (Flask framework)
- **Database**: MongoDB (NoSQL)
  
---

## Database Structure 🗂️

### **Collections in MongoDB**

1. **Books**: Stores information about books available in the store.
   ```json
   {
       "_id": "number",                  // Unique identifier for the book
       "title": "string",                // Title of the book
       "isbn": "string",                 // ISBN number of the book
       "pageCount": "number",            // Number of pages
       "publishedDate": {                // Date of publication
           "$date": "ISODate"
       },
       "longDescription": "string",      // Detailed description of the book
       "status": "string",               // Status of the book (e.g., "PUBLISH")
       "authors": ["string"],            // List of authors
       "categories": ["string"],         // Categories or genres of the book
       "quantity": "number"              // Number of copies available in stock
   }
   
2. **Orders**: Tracks orders placed by users.
   ```json
   {
    "_id": { "$oid": "string" },      // Unique identifier for the order
    "user_id": "string",              // Reference to the user who placed the order
    "items": [                        // List of items in the order
        {
            "isbn": "string",         // ISBN number of the book
            "title": "string",        // Title of the book
            "author": "string",       // Author of the book
            "price": "number",        // Price of the book
            "thumbnailUrl": "string", // URL for the book's thumbnail image
            "quantity": "number"      // Quantity of the book ordered
        }
    ],
    "total_price": "number",          // Total price of the order
    "created_at": {                   // Timestamp of the order
        "$date": "ISODate"
    },
    "status": "string"                // Status of the order (e.g., "accepted")
}

  
3. **Users**: Stores user information.
   ```json
   {
    "_id": { "$oid": "string" },      // Unique identifier for the user
    "name": "string",                 // Name of the user
    "email": "string",                // Email address
    "username": "string",             // Username for login
    "password": "string",             // Hashed password
    "role": "string",                 // Role of the user (e.g., "customer", "admin")
    "cart_details": [                 // Details of items in the user's cart
        {
            "isbn": "string",         // ISBN of the book
            "title": "string",        // Title of the book
            "quantity": "number"      // Quantity added to the cart
        }
    ]
  }

---
   
## Getting Started 🚀

### Prerequisites ⚡
To get started with this project, ensure you have the following installed:
- **Python 3.x** – Download it from [here](https://www.python.org/downloads/).
- **pip** – Python package manager (should come with Python installation).
- **MongoDB**: Install MongoDB (https://www.mongodb.com/docs/manual/installation/).

---

### Installation 🛠️

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hajistha468/online-bookstore.git
   cd online-bookstore
2. **Install dependencies: Make sure you have all the required dependencies by installing them with pip**:
    ```bash
    pip install -r requirements.txt
3. **Setup MongoDB**:
   -Start your MongoDB server locally or use a cloud MongoDB service (e.g., MongoDB Atlas).
    -Create the required collections: users, books, and orders.
4. **Run the application: Start the Flask development server**:
    ```bash
    python app.py
5. **Access the website: Open your browser and go to http://localhost:5000 to view the online bookstore.**

---
### Additional Notes:

- **Interactive User Experience**: With intuitive navigation and smooth interactions, users can easily browse and purchase their favorite books.
- **Admin Dashboard**: Admins have an easy-to-use interface to manage books and track orders efficiently.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
