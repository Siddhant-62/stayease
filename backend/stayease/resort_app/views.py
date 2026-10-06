from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Sum, Q
from .models import Resort, Booking
from datetime import datetime, timedelta
import json

# Create your views here.

# Home view - Enhanced with more data
def home(request):
    try:
        # Get featured resorts (top rated or newest)
        featured_resorts = Resort.objects.all()[:6]
        
        # Get popular destinations (unique locations)
        popular_destinations = Resort.objects.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:6]
        
        # Get top rated resorts
        top_rated_resorts = Resort.objects.all().order_by('-rating')[:3]
        
        # Get total bookings count
        total_bookings = Booking.objects.count()
        
        # Statistics for the counter section
        stats = {
            'resorts_count': Resort.objects.count(),
            'locations_count': Resort.objects.values('location').distinct().count(),
            'happy_customers': total_bookings + 15000,
            'awards': 25,
        }
        
        context = {
            'featured_resorts': featured_resorts,
            'popular_destinations': popular_destinations,
            'top_rated_resorts': top_rated_resorts,
            'stats': stats,
        }
    except Exception as e:
        # Fallback if database has issues
        context = {
            'featured_resorts': [],
            'popular_destinations': [],
            'top_rated_resorts': [],
            'stats': {'resorts_count': 0, 'locations_count': 0, 'happy_customers': 15000, 'awards': 25},
        }
    
    return render(request, 'resort_app/home.html', context)

# Resort listing view
def resort_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    resorts = Resort.objects.all()
    
    if query:
        resorts = resorts.filter(Q(name__icontains=query) | Q(location__icontains=query))
    if location:
        resorts = resorts.filter(location__icontains=location)
    if min_price:
        resorts = resorts.filter(price_per_night__gte=min_price)
    if max_price:
        resorts = resorts.filter(price_per_night__lte=max_price)
    
    context = {
        'resorts': resorts,
        'search_query': query,
    }
    return render(request, 'resort_app/resorts.html', context)

# 🔴 Resort detail view - WITH AVAILABILITY CHECK
def resort_detail(request, pk):
    try:
        resort = Resort.objects.get(pk=pk)
        similar_resorts = Resort.objects.filter(location=resort.location).exclude(pk=pk)[:3]
        
        # Get today and tomorrow for default availability check
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        available_rooms = resort.get_available_rooms_count(today, tomorrow)
        
        context = {
            'resort': resort,
            'similar_resorts': similar_resorts,
            'available_rooms': available_rooms,
            'is_available': available_rooms > 0,
        }
        return render(request, 'resort_app/resort_detail.html', context)
    except Resort.DoesNotExist:
        messages.error(request, 'Resort not found!')
        return redirect('resorts')

# About us view
def about_us(request):
    try:
        stats = {
            'resorts_count': Resort.objects.count(),
            'bookings_count': Booking.objects.count(),
            'locations_count': Resort.objects.values('location').distinct().count(),
        }
    except:
        stats = {'resorts_count': 0, 'bookings_count': 0, 'locations_count': 0}
    
    return render(request, 'resort_app/aboutus.html', {'stats': stats})

# Contact view
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'General Inquiry')
        message = request.POST.get('message')
        
        messages.success(request, f'Thank you {name}! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'resort_app/contact.html')

# 🔴 Booking view - WITH AVAILABILITY CHECK (ONLY ONE VERSION)
@login_required(login_url='login')
def booking(request):
    if request.method == 'POST':
        resort_id = request.POST.get('resort')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')
        rooms_requested = int(request.POST.get('rooms', 1))
        
        try:
            resort = Resort.objects.get(id=resort_id)
            
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            days = (check_out_date - check_in_date).days
            
            if days <= 0:
                messages.error(request, 'Check-out date must be after check-in date.')
                return redirect('booking')
            
            # 🔴 CHECK ROOM AVAILABILITY
            available = resort.get_available_rooms_count(check_in, check_out)
            
            if available < rooms_requested:
                messages.error(request, f'❌ Sorry! Only {available} room(s) available for these dates. You requested {rooms_requested}.')
                return redirect('booking')
            
            total_price = days * resort.price_per_night * rooms_requested
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                resort=resort,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                rooms_booked=rooms_requested,
                total_price=total_price,
                status='pending'
            )
            
            messages.success(request, f'✅ Booking confirmed! Booking ID: #{booking.id}. Total: ₹{total_price}')
            return redirect('my_bookings')
            
        except Resort.DoesNotExist:
            messages.error(request, 'Selected resort not found.')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
    
    resorts = Resort.objects.all()
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5] if request.user.is_authenticated else []
    
    context = {
        'resorts': resorts,
        'user_bookings': user_bookings,
        'today': datetime.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'resort_app/booking.html', context)

# My Bookings view
@login_required(login_url='login')
def my_bookings(request):
    try:
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        
        upcoming = bookings.filter(status='pending', check_in__gte=datetime.now().date())
        confirmed = bookings.filter(status='confirmed')
        past = bookings.filter(check_out__lt=datetime.now().date())
        cancelled = bookings.filter(status='cancelled')
        
        context = {
            'bookings': bookings,
            'upcoming': upcoming,
            'confirmed': confirmed,
            'past': past,
            'cancelled': cancelled,
        }
    except Exception as e:
        context = {
            'bookings': [],
            'upcoming': [],
            'confirmed': [],
            'past': [],
            'cancelled': [],
        }
        messages.error(request, f'Error loading bookings: {str(e)}')
    
    return render(request, 'resort_app/my_bookings.html', context)

# Cancel booking view
@login_required(login_url='login')
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
        
        if booking.check_in > datetime.now().date() + timedelta(days=1):
            # 🔴 Free up rooms when cancelling
            if booking.status == 'confirmed':
                booking.resort.available_rooms += booking.rooms_booked
                booking.resort.save()
            
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f'Booking #{booking.id} has been cancelled.')
        else:
            messages.error(request, 'Bookings can only be cancelled at least 24 hours before check-in.')
            
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
    
    return redirect('my_bookings')

# Authentication views
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to StayEase!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    return render(request, 'resort_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'resort_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# API Views
@require_http_methods(["GET"])
def api_resort_list(request):
    resorts = list(Resort.objects.values(
        'id', 'name', 'location', 'price_per_night', 'description', 'rating', 'amenities',
        'total_rooms', 'available_rooms'  # 🔴 Added room info to API
    ))
    return JsonResponse({'resorts': resorts, 'count': len(resorts)})

@require_http_methods(["GET"])
def api_resort_detail(request, pk):
    try:
        resort = Resort.objects.values(
            'id', 'name', 'location', 'price_per_night', 'description', 'rating', 'amenities',
            'total_rooms', 'available_rooms'  # 🔴 Added room info to API
        ).get(pk=pk)
        return JsonResponse({'resort': resort})
    except Resort.DoesNotExist:
        return JsonResponse({'error': 'Resort not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_booking(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        resort = Resort.objects.get(id=data['resort_id'])
        rooms_requested = data.get('rooms_booked', 1)
        
        # 🔴 Check availability for API
        available = resort.get_available_rooms_count(data['check_in'], data['check_out'])
        if available < rooms_requested:
            return JsonResponse({'error': f'Only {available} room(s) available'}, status=400)
        
        booking = Booking.objects.create(
            user=request.user,
            resort=resort,
            check_in=data['check_in'],
            check_out=data['check_out'],
            guests=data.get('guests', 1),
            rooms_booked=rooms_requested,
            total_price=data['total_price'],
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'message': 'Booking created successfully'
        })
    except Resort.DoesNotExist:
        return JsonResponse({'error': 'Resort not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# API for user's bookings
@require_http_methods(["GET"])
def api_my_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    bookings = list(Booking.objects.filter(user=request.user).values(
        'id', 'resort__name', 'check_in', 'check_out', 'guests', 'rooms_booked',
        'total_price', 'status', 'created_at'
    ).order_by('-created_at'))
    
    return JsonResponse({'bookings': bookings, 'count': len(bookings)})

# API to check resort availability
@require_http_methods(["GET"])
def api_check_availability(request, resort_id):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    rooms_requested = int(request.GET.get('rooms', 1))
    
    if not check_in or not check_out:
        return JsonResponse({'error': 'Check-in and check-out dates required'}, status=400)
    
    try:
        resort = Resort.objects.get(id=resort_id)
        available = resort.get_available_rooms_count(check_in, check_out)
        
        return JsonResponse({
            'available': available >= rooms_requested,
            'available_rooms': available,
            'requested_rooms': rooms_requested
        })
    except Resort.DoesNotExist:
        return JsonResponse({'error': 'Resort not found'}, status=404)