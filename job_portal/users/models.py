from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils import timezone

USER_ROLES = (
    ('admin', 'Admin'),
    ('recruiter', 'Recruiter'),
    ('candidate', 'Candidate'),
    ('trainer', 'Trainer'),
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)
    role = models.CharField(choices=USER_ROLES, max_length=20, default='candidate')
    
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['role']  

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.role}"
    
    
class Job(models.Model):

    class Meta:
        app_label = 'users'
        
    STATUS_CHOICES = [
        ("active" , "Active"),
        ("inactive" , "Inactive")
    ]

    title = models.CharField(max_length=100, default="")
    company = models.CharField(max_length=100, default="")
    description = models.TextField(max_length=250)
    location = models.CharField(max_length=100, default="")
    salary = models.IntegerField()
    status = models.CharField(max_length=20, choices=USER_ROLES, default='active')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_jobs")
    # position = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.title} - {self.company}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("pending","Pending"),
        ("shortlisted","Shortlisted"),
        ("reviewed","Reviewed"),
        ("rejected","Rejected"),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="job_applications")
    resume = models.URLField(blank=False)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default= "pending")
    applied_at = models.DateTimeField( default=timezone.now)
    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate.email} applied for {self.job.title}"
    

class TrainerService(models.Model):
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_services')

    name = models.CharField(max_length=100)
    field = models.CharField(max_length=200)
    skills = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} (${self.price})"