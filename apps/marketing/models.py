import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from tinymce.models import HTMLField
# Create your models here.


class Notification(models.Model):

    CATEGORY_TYPES = [
        ( "personal", "Personal", ),
        ( "all", "All", ),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=255, choices=CATEGORY_TYPES, default="all")
    recipient = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlogCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



class Blog(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    category = models.ForeignKey(BlogCategory, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to="blogs/")
    exerpt = models.TextField()
    content = HTMLField()

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.category.name}")
            unique_suffix = uuid.uuid4().hex[:20]
            self.slug = f"{base_slug}-{unique_suffix}-kenautos-hub-car-news-and-blogs-in-kenya"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

