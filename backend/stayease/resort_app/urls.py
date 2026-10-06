from django.urls import path
from . import views

urlpatterns = [
    # Template views
    path('', views.resort_list, name='resorts'),
    path('<int:pk>/', views.resort_detail, name='resort_detail'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views.booking, name='booking'),
    
    # 🔴 NEW: My Bookings and Cancel Booking
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/resorts/', views.api_resort_list, name='api_resort_list'),
    path('api/resorts/<int:pk>/', views.api_resort_detail, name='api_resort_detail'),
    path('api/bookings/create/', views.api_create_booking, name='api_create_booking'),
    
    # 🔴 NEW: Additional API endpoints
    path('api/my-bookings/', views.api_my_bookings, name='api_my_bookings'),
    path('api/check-availability/<int:resort_id>/', views.api_check_availability, name='api_check_availability'),
]