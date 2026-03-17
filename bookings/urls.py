from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('book/', views.book_service, name='book_service'),

    path('confirm-booking/', views.confirm_booking, name='confirm_booking'),

    path('my-bookings/', views.my_bookings, name='my_bookings'),

    path('booking/<int:id>/', views.booking_detail, name='booking_detail'),

    
    path('admin-panel/',                         views.admin_dashboard,      name='admin_dashboard'),
    path('admin-panel/booking/<int:id>/',        views.admin_booking_detail, name='admin_booking_detail'),
    path('admin-panel/customers/',               views.admin_customers,      name='admin_customers'),

]