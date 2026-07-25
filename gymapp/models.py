from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# Create your models here.

class User(AbstractUser): #username, email, password, first_name, last_name are inbuilt
  ROLE_CHOICES = [
    ('ADMIN','Admin'),
    ('MEMBER','Member'),
  ]
  role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='MEMBER')
  phone = models.CharField(max_length=15,blank=True)

  def __str__(self):
    return f"{self.username} ({self.role})"
    
class MembershipPlan(models.Model):
  name = models.CharField(max_length=100)
  duration_months = models.PositiveIntegerField()
  fee = models.DecimalField(max_digits=6,decimal_places=2)
  description = models.TextField(blank=True)

  def __str__(self):
    return f"{self.name} - {self.duration_months} months - {self.fee}"
  
class Trainer(models.Model):
  name = models.CharField(max_length=100)
  mobile = models.CharField(max_length=15)
  specialization = models.CharField(max_length=200)
  shift_timing = models.CharField(max_length=200)

  def __str__(self):
    return f"{self.name} - {self.specialization}"
    
class MemberProfile(models.Model):
  GENDER_CHOICES = (
    ('MALE','Male'),
    ('FEMALE','Female'),
    ('OTHER','Other')
  )
  user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name = 'member_profile')
  full_name = models.CharField(max_length=100)
  mobile = models.CharField(max_length=15)
  age = models.PositiveIntegerField(null=True,blank=True)
  gender = models.CharField(max_length=10,choices=GENDER_CHOICES, null=True,blank=True)
  address = models.TextField(blank=True)
  join_date = models.DateField(default=timezone.now)
  plan = models.ForeignKey(MembershipPlan,on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
  trainer = models.ForeignKey(Trainer,on_delete=models.SET_NULL,null=True,blank=True,related_name='members')
  membership_start = models.DateField(null=True,blank=True)
  membership_end = models.DateField(null=True,blank=True)

  def __str__(self):
    return f"{self.full_name} - {self.user.username}"    #Here complete
  
class Equipment(models.Model):
  name = models.CharField(max_length=100)
  units = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=8, decimal_places=2)
  purchase_date = models.DateField(default=timezone.now)
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return f"{self.name} (Units: {self.units})"
    
class Payment(models.Model):
  PAYMENT_MODE_CHOICES = (
    ('CASH','Cash'),
    ('ONLINE','Online'),
  )
  PAYMENT_STATUS_CHOICES = (
    ('PAID','Paid'),
    ('PENDING','Pending'),
    ('FAILED','Failed'),
  )
  member = models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='payment')
  plan = models.ForeignKey(MembershipPlan,on_delete=models.SET_NULL,null=True,blank=True,related_name='payments')
  amount = models.DecimalField(max_digits=8,decimal_places=2)
  payment_date = models.DateField(default=timezone.now)
  mode = models.CharField(max_length=50,choices=PAYMENT_MODE_CHOICES)
  status = models.CharField(max_length=50,choices=PAYMENT_STATUS_CHOICES)
  notes = models.TextField(blank=True)

  def __str__(self):
    return f"Payment of ${self.amount} by {self.member.full_name} on {self.payment_date}"

class Attendance(models.Model):
  member = models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='attendances')
  date = models.DateField(default=timezone.now)
  time_in = models.TimeField(null=True,blank=True)

  class Meta:
    unique_together = ('member','date')

  def __str__(self):
    return f"{self.member.full_name} - {self.date} - {self.time_in}" 

class Enquiry(models.Model):
  ENQUIRY_STATUS_CHOICES = (
    ('NEW','New'),
    ('SEEN','Seen'),
    ('RESOLVED','Resolved'),
  )
  name = models.CharField(max_length=100)
  email = models.EmailField()
  mobile = models.CharField(max_length=15)
  message = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=20,choices=ENQUIRY_STATUS_CHOICES,default='NEW')

  def __str__(self):
    return f"Enquiry from {self.name} - {self.email} - Status: {self.status}"

class WorkoutPlan(models.Model):
  member = models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='workout_plans')
  title = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  created_at  =models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.title} - Created at: {self.created_at}"
  
class Feedback(models.Model):
  member = models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='feedback')
  message = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Feedback from {self.member.full_name} - Created at: {self.created_at}"
  

