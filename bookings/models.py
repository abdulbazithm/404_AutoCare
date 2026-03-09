from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver


SERVICE_CHOICES = [
    ('parking_only', 'Parking Only'),
    ('parking_wash', 'Parking + Car Wash'),
    ('parking_interior', 'Parking + Interior Cleaning'),
    ('parking_ceramic', 'Parking + Ceramic Coating'),
]


SERVICE_PRICES = {
    'parking_only': 500,
    'parking_wash': 800,
    'parking_interior': 1000,
    'parking_ceramic': 4000,
}


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('received', 'Car Received'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('ready', 'Ready For Pickup'),
]

AIRPORT_CHOICES = [
    ('TRV', 'Trivandrum International Airport'),
    ('COK', 'Cochin International Airport'),
]


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Booking(models.Model):

    booking_id = models.CharField(max_length=20, unique=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    car_model = models.CharField(max_length=100)
    car_number = models.CharField(max_length=20)

    airport = models.CharField(max_length=200, choices=AIRPORT_CHOICES)
    


    parking_date = models.DateField()
    return_date = models.DateField()

    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)

    price = models.IntegerField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):

        # Auto generate booking id
        if not self.booking_id:
            year = datetime.date.today().year
            last_booking = Booking.objects.filter(
                booking_id__contains=year
            ).count() + 1

            self.booking_id = f"AC-{year}-{str(last_booking).zfill(3)}"

        # Auto set price
        self.price = SERVICE_PRICES.get(self.service_type)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_id


class ServiceProgress(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    car_received = models.BooleanField(default=False)

    exterior_wash = models.BooleanField(default=False)

    interior_clean = models.BooleanField(default=False)

    ceramic_coating = models.BooleanField(default=False)

    ready_for_pickup = models.BooleanField(default=False)

    def __str__(self):
        return f"Progress - {self.booking.booking_id}"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)