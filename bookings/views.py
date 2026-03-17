from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from .forms import RegisterForm, BookingForm
from .models import Booking, ServiceProgress, Profile, STATUS_CHOICES  # ✅ STATUS_CHOICES added


def home(request):
    return render(request, 'home.html')


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            user.profile.phone = form.cleaned_data['phone']
            user.profile.save()

            login(request, user)
            return redirect('home')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):

    error = None

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect('admin_dashboard')

            return redirect('home')

        else:
            # ✅ Authentication failed — set error and fall through to render
            error = 'Invalid username or password.'

    # ✅ Runs on GET and on failed POST
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def book_service(request):

    if request.method == 'POST':

        form = BookingForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            request.session['booking_data'] = {
                'car_model':    data['car_model'],
                'car_number':   data['car_number'],
                'airport':      data['airport'],
                'parking_date': str(data['parking_date']),
                'return_date':  str(data['return_date']),
                'service_type': data['service_type'],
            }

            return redirect('confirm_booking')

    else:
        form = BookingForm()

    return render(request, 'booking_form.html', {'form': form})


@login_required
def confirm_booking(request):

    data = request.session.get('booking_data')

    if not data:
        return redirect('book_service')

    service_prices = {
        'parking_only':     500,
        'parking_wash':     800,
        'parking_interior': 1000,
        'parking_ceramic':  4000,
    }

    price = service_prices.get(data['service_type'])

    if request.method == 'POST':

        booking = Booking.objects.create(
            user=request.user,
            car_model=data['car_model'],
            car_number=data['car_number'],
            airport=data['airport'],
            parking_date=data['parking_date'],
            return_date=data['return_date'],
            service_type=data['service_type'],
            price=price
        )

        ServiceProgress.objects.create(booking=booking)
        return redirect('my_bookings')

    return render(request, 'confirm_booking.html', {
        'data':  data,
        'price': price
    })


@login_required
def my_bookings(request):

    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, id):

    booking  = get_object_or_404(Booking, id=id, user=request.user)  # ✅ security fix
    progress = ServiceProgress.objects.get(booking=booking)

    return render(request, 'booking_detail.html', {
        'booking':  booking,
        'progress': progress
    })


# ── Admin views ────────────────────────────────────────────────────


@staff_member_required
def admin_dashboard(request):

    total_bookings  = Booking.objects.count()
    total_revenue   = Booking.objects.aggregate(Sum('price'))['price__sum'] or 0
    pending_count   = Booking.objects.filter(status='pending').count()
    completed_count = Booking.objects.filter(status='completed').count()
    bookings        = Booking.objects.all().order_by('-created_at')

    return render(request, 'admin_dashboard.html', {
        'total_bookings':  total_bookings,
        'total_revenue':   total_revenue,
        'pending_count':   pending_count,
        'completed_count': completed_count,
        'bookings':        bookings,
    })


@staff_member_required
def admin_booking_detail(request, id):

    booking  = get_object_or_404(Booking, id=id)
    progress = ServiceProgress.objects.get(booking=booking)

    if request.method == 'POST':

        new_status = request.POST.get('status')
        if new_status:
            booking.status = new_status
            booking.save()

        progress.car_received     = 'car_received'     in request.POST
        progress.exterior_wash    = 'exterior_wash'    in request.POST
        progress.interior_clean   = 'interior_clean'   in request.POST
        progress.ceramic_coating  = 'ceramic_coating'  in request.POST
        progress.ready_for_pickup = 'ready_for_pickup' in request.POST
        progress.save()

        # ✅ ?saved=1 triggers the success toast
        return redirect(f"/admin-panel/booking/{id}/?saved=1")

    return render(request, 'admin_booking_detail.html', {
        'booking':  booking,
        'progress': progress,
        'statuses': STATUS_CHOICES,
    })


@staff_member_required
def admin_customers(request):

    profiles = Profile.objects.select_related('user').annotate(  # ✅ single clean query
        booking_count=Count('user__booking')
    ).order_by('-user__date_joined')

    return render(request, 'admin_customers.html', {
        'profiles': profiles,
    })
