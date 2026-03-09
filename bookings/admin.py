from django.contrib import admin
from .models import Booking, ServiceProgress, Profile

admin.site.register(Profile)
admin.site.register(Booking)
admin.site.register(ServiceProgress)