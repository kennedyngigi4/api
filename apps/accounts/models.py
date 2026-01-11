import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.


class Package(models.Model):

    PACKAGE_TYPE_CHOICES = [
        ( "car", "Car", ),
        ( "bike", "Bike", ),
        ( "spare parts", "Spare Parts", ),
    ]

    pid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    is_discounted = models.BooleanField(default=False, null=True, blank=True)
    discounted_price = models.IntegerField(null=True, blank=True)
    active_days = models.IntegerField(null=True, blank=True)
    renew_after_hours = models.IntegerField(null=True, blank=True)
    uploads_allowed = models.IntegerField() #number of vehicles one can upload
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None):
        if not email:
            raise ValueError("Email is required")
        
        user = self.model(
            email=self.normalize_email(email).lower(),
            name=name,
            phone=phone
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user


    def create_superuser(self, email, name, phone, password=None):
        if not email:
            raise ValueError("Email is required")
        
        user = self.create_user(
            email=self.normalize_email(email).lower(),
            name=name,
            phone=phone,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user




def profileImagePath(instance, filename):
    return f"users/{instance.uid}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):

    gender_choices = (
        ( "Female", "Female", ),
        ( "Male", "Male", ),
        ( "Prefer not to say", "Prefer not to say", ),
    )

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    email = models.EmailField(null=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=60, null=True, unique=True)
    gender = models.CharField(max_length=100, null=True, blank=True)

    image = models.ImageField(upload_to=profileImagePath, null=True, blank=True)

    is_partner = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    free_limit = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name","phone"
    ]

    def __str__(self):
        return f"{self.email}"



def businessImagesPath(instance, filename):
    uid = str(instance.user.uid).replace("-",""),
    return f"users/{uid}/{filename}"


class UserBusiness(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    
    user = models.OneToOneField(User, related_name="business", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=65, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    website = models.URLField(max_length=355, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    latlng = models.CharField(max_length=255, null=True, blank=True)
    
    image = models.ImageField(upload_to=businessImagesPath, null=True, blank=True)
    banner = models.ImageField(upload_to=businessImagesPath, null=True, blank=True)
    
    facebook = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    tiktok = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return self.name



class Subscription(models.Model):
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    uploads_used = models.IntegerField(default=0)
    end_date = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        if self.uploads_used < self.package.uploads_allowed:
            return True
        
        
    def has_uploads_left(self):
        return self.uploads_used < self.package.uploads_allowed
    
    def increment_uploads(self):
        if self.has_uploads_left():
            self.uploads_used += 1
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user} {self.package.name} ({self.uploads_used}/{self.package.uploads_allowed})"

