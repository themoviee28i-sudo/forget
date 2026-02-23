# Bakery Shop Web Application

A professional, full-featured bakery shop web application built with Python Flask, SQLite, and Bootstrap 5.

## Features

### 🔐 Admin System
- **Secure Login**: Hardcoded admin credentials (username: `admin`, password: `1234`)
- **Session Protection**: Secure session-based authentication for admin routes
- **Logout Function**: Secure logout with session clearing

### 🛍️ Product Management (CRUD)
- **Add Products**: Upload products with images, names, and prices
- **Edit Products**: Update existing products and images
- **Delete Products**: Remove products from inventory
- **Image Handling**: Secure file uploads with validation (PNG, JPG, JPEG, GIF)

### 🏠 Homepage
- **Product Display**: Bootstrap cards with product images, names, and prices
- **Responsive Layout**: Mobile-friendly design
- **Quick Add to Cart**: One-click product addition

### 🛒 Shopping Cart System
- **Session-Based Cart**: Shopping cart stored in user sessions
- **Quantity Management**: Increase/decrease product quantities
- **Cart Summary**: Real-time total calculation
- **Remove Items**: Remove specific products from cart

### 💳 Checkout System
- **Customer Information**: Name and email collection
- **Payment Options**: Three payment methods (Cash, Bank Transfer, QR Code)
- **Order Confirmation**: Order summary and success page
- **Order Tracking**: Confirmation with details

### 📊 Admin Dashboard
- **Overview Statistics**: Total products and management
- **Product Table**: View all products with images and prices
- **Action Buttons**: Quick edit and delete functionality
- **Order Management**: View all customer orders

## Technology Stack

- **Backend**: Python 3 with Flask
- **Database**: SQLite (auto-initializes on first run)
- **Frontend**: Bootstrap 5 CDN
- **Icons**: Font Awesome 6
- **Session Management**: Flask sessions
- **File Handling**: Werkzeug secure_filename

## Installation & Setup

### Prerequisites
- Python 3.7 or higher

### Step 1: Install Dependencies
```
pip install -r requirements.txt
```

### Step 2: Run the Application
```
python app.py
```

### Step 3: Access the Application
Open your web browser and navigate to: http://localhost:5000

## Default Admin Credentials
- Username: admin
- Password: 1234

## File Structure
- app.py - Main Flask application
- templates/ - HTML templates
- static/uploads/ - Product image storage
- bakery.db - SQLite database (auto-created)

## Features Included
✅ Admin login with session protection
✅ Product management (CRUD operations)
✅ Secure image upload with validation
✅ Session-based shopping cart
✅ Checkout system with payment options
✅ Order management
✅ Responsive Bootstrap 5 UI
✅ Error handling (404, 500 pages)

---

**Version**: 1.0.0 | **Python**: 3.7+ | **Flask**: 2.3.0+

Enjoy your Bakery Shop application! 🎂