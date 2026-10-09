StayEase

StayEase is a full-stack resort booking web application built with Django and MySQL. Users can browse and search resorts, check real-time room availability for their dates, book rooms, and manage their bookings. Staff manage resorts, rooms and bookings from a customized Django admin dashboard.

Features

For guests

Browse resorts with search by name or location, plus filters for location and price range
Resort detail page with amenities, rating, available rooms and similar resorts in the same location
Sign up, log in and log out with Django authentication
Book one or more rooms for a date range, with automatic price calculation (nights x price per night x rooms)
Real-time availability check on the booking page using the Fetch API (AJAX), so a booking cannot exceed the rooms left for the chosen dates
"My Bookings" page that groups bookings as upcoming, confirmed, past and cancelled
Cancel a booking from the app (allowed only when check-in is more than 24 hours away)
Contact and About Us pages

For staff (Django admin)

Manage resorts: name, location, description, price, rating, image, amenities, total rooms
Available rooms are recalculated automatically when total rooms change
Manage bookings with filters, search and inline status editing
Bulk actions to confirm or cancel selected bookings; room counts update with the action

JSON API

REST-style endpoints for resorts, bookings and availability (see API endpoints)
Tech stack
Layer	Technology
Backend	Python, Django 5.2
Database	MySQL (via mysqlclient)
Frontend	Django templates, HTML5, CSS3, JavaScript, Bootstrap 5.3, Font Awesome
Images	Pillow (resort photo uploads)
Auth	Django built-in authentication
Project structure
stayease/
├── backend/
│   └── stayease/
│       ├── manage.py
│       ├── stayease/          # project settings, root URLs, WSGI/ASGI
│       └── resort_app/        # models, views, URLs, admin, migrations
├── frontend/
│   ├── templates/resort_app/  # base, home, resorts, resort_detail, booking,
│   │                          # my_bookings, login, signup, aboutus, contact
│   └── static/                # css, js, images
└── media/resorts/             # uploaded resort images
Data model
Resort: name, location, description, price_per_night, image, rating, amenities, total_rooms, available_rooms, timestamps. Provides check_availability() and get_available_rooms_count() which count overlapping pending and confirmed bookings for a date range.
Booking: user, resort, check_in, check_out, guests, rooms_booked, total_price, status (pending, confirmed, cancelled), created_at.
Getting started
Prerequisites
Python 3.10 or newer
MySQL Server 8 or newer
Build tools needed by mysqlclient (see the mysqlclient install notes for your OS)
Setup
Clone the repository
bash
   git clone https://github.com/Siddhant-62/stayease.git
   cd stayease
Create and activate a virtual environment
bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
Install dependencies
bash
   pip install django mysqlclient pillow
Create the MySQL database
sql
   CREATE DATABASE stayease_db CHARACTER SET utf8mb4;
Configure the database connection in backend/stayease/stayease/settings.py:
python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'stayease_db',
           'USER': 'your_mysql_user',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
Run migrations and create an admin user
bash
   cd backend/stayease
   python manage.py migrate
   python manage.py createsuperuser
Start the development server
bash
   python manage.py runserver
Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for the admin dashboard. Add a few resorts (with images) in the admin before booking.
Pages and routes
URL	Description
/	Home with featured and top-rated resorts and stats
/resorts/	Resort listing with search and filters (q, location, min_price, max_price)
/resorts/<id>/	Resort detail
/resorts/booking/	Book rooms (login required)
/resorts/my-bookings/	Your bookings (login required)
/resorts/cancel-booking/<id>/	Cancel a booking (login required)
/resorts/signup/, /resorts/login/, /resorts/logout/	Authentication
/resorts/about/, /resorts/contact/	Info pages
/admin/	Admin dashboard
API endpoints

All endpoints are under /resorts/api/.

Method	Endpoint	Description
GET	/resorts/api/resorts/	List all resorts
GET	/resorts/api/resorts/<id>/	Resort details
GET	/resorts/api/check-availability/<resort_id>/?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&rooms=1	Check room availability for a date range
GET	/resorts/api/my-bookings/	Current user's bookings (login required)
POST	/resorts/api/bookings/create/	Create a booking from JSON (login required)

Example availability response:

json
{
  "available": true,
  "available_rooms": 8,
  "requested_rooms": 1
}
Notes for production

This project is set up for local development. Before deploying:

Set DEBUG = False and update ALLOWED_HOSTS
Move SECRET_KEY and the database credentials into environment variables
Run python manage.py collectstatic and serve static and media files with a web server
Author

Siddhant Kumar GitHub: @Siddhant-62
