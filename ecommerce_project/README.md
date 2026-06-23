# eCommerce Django Application

## Project Overview
A Django-based eCommerce platform that supports vendors and buyers, store and product management, shopping carts, checkout, reviews, and email notifications.

## Features
- Vendor and Buyer user roles
- Vendor store and product management
- Buyer shopping cart and checkout
- Verified and unverified product reviews
- Email-based checkout invoices
- Password reset via email with expiring tokens
- MariaDB database backend
- Django authentication and permissions

## Tech Stack
- Python 3.x
- Django 4.x
- MariaDB
- HTML/CSS (Django Templates)
- Django ORM

## Getting the Project
This project is hosted on my GitHub profile. Clone the repository and enter the project folder as shown below.

git clone https://github.com/char-rea/eccomerceapplication
cd ecommerce_project

If you fork or rename the repository, update the URL and folder name accordingly.

## Installation Instructions

### 1. Create and activate a virtual environment
python -m venv venv  
source venv/bin/activate   # macOS/Linux  
venv\Scripts\activate      # Windows  

### 2. Install dependencies
pip install -r requirements.txt

### 3. Install MariaDB
sudo apt install mariadb-server        # Linux  
brew install mariadb                   # macOS  

### 4. Create the database
mysql -u root -p

CREATE DATABASE ecommerce_db;  
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'password';  
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'django_user'@'localhost';  
FLUSH PRIVILEGES;  

### 5. Configure Django settings
This project does not use environment variables. Update credentials directly in settings.py.

Database configuration (settings.py):

DATABASES = {  
&nbsp;&nbsp;&nbsp;&nbsp;'default': {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ENGINE': 'django.db.backends.mysql',  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'NAME': 'ecommerce_db',  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'USER': 'django_user',  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'PASSWORD': 'password',  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'HOST': 'localhost',  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'PORT': '3306',  
&nbsp;&nbsp;&nbsp;&nbsp;}  
}

Email configuration (settings.py):

EMAIL_HOST = 'smtp.gmail.com'  
EMAIL_PORT = 587  
EMAIL_USE_TLS = True  
EMAIL_HOST_USER = 'your_email@gmail.com'  
EMAIL_HOST_PASSWORD = 'your_app_password'  

### 6. Run migrations
python manage.py makemigrations  
python manage.py migrate  

### 7. Create a superuser
python manage.py createsuperuser

### 8. Run the development server
python manage.py runserver

Open your browser and navigate to:  
http://127.0.0.1:8000/

## Database Migration Verification
The application was migrated from SQLite to MariaDB. Migration and connectivity were verified using Django’s database shell.

python manage.py dbshell

If the old SQLite database exists, remove it:

rm db.sqlite3

## API 

This project exposes a small REST API using Django REST Framework to support data retrieval for vendors and buyers.

The API is separated from the web application views and does not interfere with the frontend.

Available API Routes

Method	Endpoint	Description
GET	/api/stores/	Retrieve all stores
GET	/api/products/	Retrieve all products
GET	/api/vendors/	Retrieve vendors with their stores and products
GET	/api/reviews/	Retrieve reviews for the authenticated vendor’s products
GET	/api/vendor/products-with-reviews/	Retrieve only products that have reviews (vendor only)
POST	/api/stores/add/	Create a new store (authenticated vendor)
PUT	/api/stores/<id>/edit/	Update a store owned by the authenticated vendor
DELETE	/api/stores/<id>/delete/	Delete a store owned by the authenticated vendor

Authentication
The API uses Django session authentication and Basic Authentication.
Endpoints that modify data require an authenticated user.
Read‑only endpoints are publicly accessible unless stated otherwise.

Example API Request:
GET http://127.0.0.1:8000/api/products/