document.addEventListener("DOMContentLoaded", function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar background change on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = '#ffffff';
            navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        } else {
            navbar.style.backgroundColor = 'transparent';
            navbar.style.boxShadow = 'none';
        }
    });

    // Show welcome modal for new users (after 5 seconds)
    if (!localStorage.getItem('modalShown')) {
        setTimeout(function() {
            var authModal = new bootstrap.Modal(document.getElementById('authModal'));
            authModal.show();
            localStorage.setItem('modalShown', 'true');
        }, 5000);
    }

    // Add to cart animation
    const bookButtons = document.querySelectorAll('.btn-primary');
    bookButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('no-animation')) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                setTimeout(() => {
                    this.innerHTML = 'Book Now';
                }, 2000);
            }
        });
    });

    // Price calculator for booking page
    const checkIn = document.getElementById('check_in');
    const checkOut = document.getElementById('check_out');
    const resortSelect = document.getElementById('resort');
    
    if (checkIn && checkOut && resortSelect) {
        function calculatePrice() {
            const start = new Date(checkIn.value);
            const end = new Date(checkOut.value);
            const days = (end - start) / (1000 * 60 * 60 * 24);
            
            if (days > 0 && resortSelect.value) {
                const pricePerNight = resortSelect.options[resortSelect.selectedIndex].text.match(/\$(\d+)/);
                if (pricePerNight) {
                    const total = days * parseInt(pricePerNight[1]);
                    document.getElementById('total-price').textContent = `$${total}`;
                }
            }
        }
        
        checkIn.addEventListener('change', calculatePrice);
        checkOut.addEventListener('change', calculatePrice);
        resortSelect.addEventListener('change', calculatePrice);
    }

    // Image gallery lightbox
    const galleryImages = document.querySelectorAll('.gallery-img');
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('imageModal'));
            document.getElementById('modalImage').src = this.src;
            modal.show();
        });
    });

    // Lazy loading images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// API calls
const API = {
    async getResorts() {
        try {
            const response = await fetch('/api/resorts/');
            return await response.json();
        } catch (error) {
            console.error('Error fetching resorts:', error);
            return [];
        }
    },
    
    async createBooking(bookingData) {
        try {
            const response = await fetch('/api/bookings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(bookingData)
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating booking:', error);
            return null;
        }
    }
};

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}