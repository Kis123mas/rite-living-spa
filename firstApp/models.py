from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_secretary = models.BooleanField(blank=True, null=True, default=False)
    is_not_secretary = models.BooleanField(blank=True, null=True, default=False)
    is_admin = models.BooleanField(blank=True, null=True, default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # You can add more fields here like ['full_name']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Social Media Links
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} Profile'


class ServiceRendered(models.Model):
    staff_name = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_not_secretary': True})
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('pos', 'POS'),
        ('transfer', 'Transfer'),
    ]
    mode_of_payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    
    # Type of service (Solo or Contract)
    SERVICE_TYPE_CHOICES = [
        ('solo', 'Solo'),
        ('contract', 'Contract'),
    ]
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)

    # Type of service (Solo or Contract)
    SERVICE_TYPE_RENDERED = [
        ('Massage Therapy', 'Massage Therapy'),
        ('Facial Treatments', 'Facial Treatments'),
        ('Aromatherapy', 'Aromatherapy'),
        ('Body Scrubs', 'Body Scrubs'),
        ('Steam & Sauna', 'Steam & Sauna'),
        ('Nail Care', 'Nail Care'),
    ]
    service_rendered = models.CharField(max_length=20, null=True, blank=True, choices=SERVICE_TYPE_RENDERED)
    
    # Date when the service was rendered
    service_date = models.DateField(auto_now_add=True)
    
    # Additional description for the service
    description = models.TextField(null=True, blank=True)
    
    # Staff position or role for context
    staff_role = models.CharField(max_length=100, null=True, blank=True)
    
    # Optionally, the service can have a customer associated with it (if applicable)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Optional field for tracking the invoice number
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Timestamp for when the service record was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optionally, a status field to track whether the payment has been confirmed or pending
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Service Rendered by {self.staff_name} on {self.service_date} - {self.amount}"

    class Meta:
        verbose_name = "Service Rendered"
        verbose_name_plural = "Services Rendered"
        ordering = ['-service_date']


class Uniform(models.Model):
    uniform_date = models.DateField()  # Single field to store the full date
    uniform_type = models.CharField(max_length=100)
    uniform_color = models.CharField(max_length=50)
    uniform_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.uniform_type} ({self.uniform_date})"

    # You can create methods to easily access day, month, and year
    @property
    def day(self):
        return self.uniform_date.day

    @property
    def month(self):
        return self.uniform_date.month

    @property
    def year(self):
        return self.uniform_date.year

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['uniform_date'], name='unique_uniform_date')
        ]


class Expense(models.Model):
    # Categories for the expense (you can modify this list or make it dynamic)
    CATEGORY_CHOICES = [
        ('service', 'Service'),
        ('supplies', 'Supplies'),
        ('payroll', 'Payroll'),
        ('maintenance', 'Maintenance'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    # Fields for the expense model
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Stores the amount of the expense
    description = models.TextField()  # A brief description of the expense
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')  # Category of the expense
    date = models.DateTimeField(default=timezone.now)  # Date when the expense was recorded
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the expense was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of when the expense was last updated

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.date.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date']  # Ordering expenses by most recent date


class Product(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='uploads/orders/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unnamed Product"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', blank=True, null=True)
    uploaded_file = models.FileField(upload_to='uploads/orders/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name if self.product else 'No Product'} ({self.client.first_name if self.client else 'No Client'})"


class Message(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.first_name} on Order #{self.order.id}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} Star(s)"


class SpaSessionBooking(models.Model):
    SESSION_TYPE_CHOICES = [
        ('contract', 'Contract'),
        ('solo', 'Solo'),
    ]

    SERVICE_TYPE_CHOICES = [
        ('massage', 'Relaxing Massage'),
        ('facial', 'Rejuvenating Facial'),
        ('aromatic', 'Aromatic Oil Therapy'),
        ('bath', 'Lavender Bath Soak'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='spa_bookings')
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, null=True, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_type} ({self.status})"


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.first_name} {self.last_name} ({self.email})"


