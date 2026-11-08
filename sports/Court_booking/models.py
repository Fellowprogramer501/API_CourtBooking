from django.db import models
from users.models import user
from datetime import datetime,time ,timedelta
import random

class Sport(models.Model):
    name = models.CharField(max_length=50)
    hrly_rates = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.name}"

class Branch(models.Model):
    Location = models.CharField(max_length=50)
    Sports = models.ManyToManyField(Sport)
    contact_num = models.CharField(max_length=13)
    contact_email = models.CharField(max_length=50)
    location_rates = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.Location}"

class Court(models.Model):
    branch = models.ForeignKey(Branch,  on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE)
    courts = models.IntegerField(default=1)
    available_courts = models.IntegerField(null=True,blank=True)
    def save(self, *args, **kwargs):
        if self.available_courts is None:
            self.available_courts = self.courts
        else:
            if self.available_courts > self.courts:
                raise ValueError("Available courts cant be more then preasent ones")
        
        return super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.sport.name} on {self.branch.Location}"


class booking_order(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE, related_name="Booking_user")
    branch = models.ForeignKey(Branch,  on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE)
    Code = models.CharField(null=True, blank=True, max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    Date = models.DateField(default=datetime.now)
    time = models.TimeField(default= time(12,0))
    duration = models.DurationField(default = timedelta(hours=1))
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2,null=True, blank=True)
    court = models.ForeignKey(Court, on_delete= models.CASCADE, null= True, blank=True)
    court_no = models.PositiveIntegerField(default="1", null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.Date and self.time:
            self.start = datetime.combine( self.Date, self.time)
        if self.start and self.duration:
            self.end = self.start + self.duration
        

        
        duration_charge = self.duration.total_seconds()/3600
        self.cost = (self.sport.hrly_rates + self.branch.location_rates) * duration_charge
        
        
        self.Code = random.randint(1,99999)
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together=['start','end','court_no','court']
    def __str__(self):
        return f"{self.Code}"

class court_pictures(models.Model):
    court =  models.ForeignKey(Court, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Court/')
    def __str__(self):
        return f"Image for {self.court.sport.name} on {self.court.branch.Location}"

class booking_recipt(models.Model):
    booking = models.ForeignKey(booking_order, on_delete=models.CASCADE)
    client = models.ForeignKey(user,on_delete=models.CASCADE)
    Date_time = models.DateTimeField()
    End_time = models.DateTimeField()
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    cost= models.PositiveIntegerField()
    court_no = models.PositiveIntegerField()
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.booking} of {self.user}"
    