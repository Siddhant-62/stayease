from django.db import models
from django.contrib.auth.models import User


class Resort(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField(default="Luxurious resort with amazing amenities")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='resorts/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    amenities = models.TextField(default="Swimming Pool, Spa, Restaurant, WiFi")
    
    # 🔴 NEW: Room capacity fields
    total_rooms = models.IntegerField(default=10)  # Total rooms in resort
    available_rooms = models.IntegerField(default=10)  # Currently available rooms
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
    
    # 🔴 NEW: Method to check availability
    def check_availability(self, check_in, check_out):
        """Check if at least 1 room is available for given dates"""
        overlapping_bookings = Booking.objects.filter(
            resort=self,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).count()
        
        return overlapping_bookings < self.total_rooms
    
    # 🔴 NEW: Method to get available room count for specific dates
    def get_available_rooms_count(self, check_in, check_out):
        """Return number of available rooms for given dates"""
        overlapping_bookings = Booking.objects.filter(
            resort=self,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).count()
        
        return self.total_rooms - overlapping_bookings


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField(default=1)
    rooms_booked = models.IntegerField(default=1)  # 🔴 NEW: Number of rooms booked
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', 
                            choices=[('pending', 'Pending'), 
                                   ('confirmed', 'Confirmed'),
                                   ('cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.user.username} - {self.resort.name}"