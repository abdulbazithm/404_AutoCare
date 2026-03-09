from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import RegisterForm, BookingForm
from .models import Booking, ServiceProgress, Profile


def home(request):
    return render(request, 'home.html')


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            phone = form.cleaned_data['phone']

            # Profile already created by signal
            user.profile.phone = phone
            user.profile.save()

            login(request, user)

            return redirect('home')

    else:
        form = RegisterForm()

    return render(request,'register.html',{'form':form})


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')


@login_required
def book_service(request):

    if request.method == 'POST':

        form = BookingForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            request.session['booking_data'] = {
                'car_model': data['car_model'],
                'car_number': data['car_number'],
                'airport': data['airport'],
                'parking_date': str(data['parking_date']),
                'return_date': str(data['return_date']),
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
        'parking_only': 500,
        'parking_wash': 800,
        'parking_interior': 1000,
        'parking_ceramic': 4000,
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

    return render(request,'confirm_booking.html',{
        'data':data,
        'price':price
    })


@login_required
def my_bookings(request):

    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, id):

    booking = get_object_or_404(Booking, id=id)

    progress = ServiceProgress.objects.get(booking=booking)

    return render(request, 'booking_detail.html', {
        'booking': booking,
        'progress': progress
    })

def logout_view(request):
    logout(request)
    return redirect('home')