from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER = (
        ('1', 'admin'),
        ('2', 'doc'),
    )

    user_type = models.CharField(choices=USER, max_length=50, default='1')
    profile_pic = models.ImageField(upload_to='profile_pic/', null=True, blank=True)


class Specialization(models.Model):
    sname = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sname


class DoctorReg(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    mobilenumber = models.CharField(max_length=11)
    specialization_id = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    regdate_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.admin:
            return f"{self.admin.first_name} {self.admin.last_name}"
        return f"Doctor - {self.mobilenumber}"


class Appointment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    appointmentnumber = models.IntegerField(default=0)

    fullname = models.CharField(max_length=250)
    mobilenumber = models.CharField(max_length=11)
    email = models.EmailField(max_length=100)

    # ✅ FIXED (better datatype)
    date_of_appointment = models.DateField()
    time_of_appointment = models.TimeField()

    doctor_id = models.ForeignKey(DoctorReg, on_delete=models.CASCADE)

    additional_msg = models.TextField(blank=True)

    remark = models.CharField(max_length=250, default='Not Updated Yet')
    status = models.CharField(max_length=200, default='Not Updated Yet')

    prescription = models.TextField(blank=True, default='Not Prescribed Yet')
    recommendedtest = models.TextField(blank=True, default='Not Recommended Yet')

    # ✅ VIDEO CONSULTATION FEATURE
    video_link = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)

    # 💰 PAYMENT DETAILS
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='offline')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    sms_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment #{self.appointmentnumber} - {self.fullname}"


class Page(models.Model):
    pagetitle = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    aboutus = models.TextField()
    email = models.EmailField(max_length=200)
    mobilenumber = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pagetitle


class SMSLog(models.Model):
    SMS_TYPE_CHOICES = [
        ('appointment_booking', 'Appointment Booking'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('video_link', 'Video Link'),
    ]

    SMS_STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    message = models.TextField()

    sms_type = models.CharField(max_length=50, choices=SMS_TYPE_CHOICES, default='appointment_booking')
    status = models.CharField(max_length=20, choices=SMS_STATUS_CHOICES, default='pending')

    response = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS to {self.phone_number}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')

    patient_name = models.CharField(max_length=250)
    patient_phone = models.CharField(max_length=11)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)

    transaction_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    payment_date = models.DateTimeField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"