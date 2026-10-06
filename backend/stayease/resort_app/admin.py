from django.contrib import admin
from .models import Resort, Booking


@admin.register(Resort)
class ResortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'price_per_night', 'total_rooms', 'available_rooms', 'rating', 'created_at')
    list_filter = ('location', 'rating', 'created_at')
    search_fields = ('name', 'location', 'description')
    ordering = ('-created_at',)
    list_per_page = 20
    list_editable = ('total_rooms',)  # 🔴 Edit total rooms directly from list view
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'description')
        }),
        ('Pricing & Rating', {
            'fields': ('price_per_night', 'rating')
        }),
        ('🔴 Room Management', {
            'fields': ('total_rooms', 'available_rooms'),
            'description': 'Set total number of rooms. Available rooms updates automatically based on confirmed/pending bookings.'
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'available_rooms')  # 🔴 available_rooms is read-only
    
    # 🔴 Auto-update available_rooms when total_rooms changes
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Resort.objects.get(pk=obj.pk)
            if old_obj.total_rooms != obj.total_rooms:
                # Calculate currently booked rooms
                from django.db.models import Sum
                booked = Booking.objects.filter(
                    resort=obj,
                    status__in=['pending', 'confirmed']
                ).aggregate(total=Sum('rooms_booked'))['total'] or 0
                obj.available_rooms = obj.total_rooms - booked
        super().save_model(request, obj, form, change)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'resort', 'check_in', 'check_out', 
                    'guests', 'rooms_booked', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'check_out', 'created_at')
    search_fields = ('user__username', 'user__email', 'resort__name')
    list_editable = ('status',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user',)
        }),
        ('Booking Details', {
            'fields': ('resort', 'check_in', 'check_out', 'guests', 'rooms_booked')  # 🔴 Added rooms_booked
        }),
        ('Payment Information', {
            'fields': ('total_price', 'status')
        }),
    )
    
    readonly_fields = ('created_at', 'total_price')
    
    # 🔴 Custom actions for booking management
    actions = ['confirm_bookings', 'cancel_bookings']
    
    @admin.action(description="✅ Confirm selected bookings")
    def confirm_bookings(self, request, queryset):
        for booking in queryset:
            if booking.status == 'pending':
                resort = booking.resort
                # Check if enough rooms available
                if resort.available_rooms >= booking.rooms_booked:
                    booking.status = 'confirmed'
                    booking.save()
                    resort.available_rooms -= booking.rooms_booked
                    resort.save()
                    self.message_user(request, f"✅ Booking #{booking.id} confirmed.", level='success')
                else:
                    self.message_user(
                        request, 
                        f"❌ Cannot confirm Booking #{booking.id}: Only {resort.available_rooms} room(s) available.", 
                        level='error'
                    )
    
    @admin.action(description="❌ Cancel selected bookings")
    def cancel_bookings(self, request, queryset):
        for booking in queryset:
            if booking.status in ['pending', 'confirmed']:
                # If booking was confirmed, free up the rooms
                if booking.status == 'confirmed':
                    booking.resort.available_rooms += booking.rooms_booked
                    booking.resort.save()
                
                booking.status = 'cancelled'
                booking.save()
                self.message_user(request, f"❌ Booking #{booking.id} cancelled.")