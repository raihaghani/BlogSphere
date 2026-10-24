import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

def nonblank(value):
    if not value.strip():
        raise ValidationError('This field cannot be blank.')

COVERS = [(f'images/{name}.svg', name.replace('-', ' ').title()) for name in
          ['technology', 'programming', 'artificial-intelligence', 'cybersecurity', 'business']]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[nonblank])
    slug = models.SlugField(max_length=120, unique=True)
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name

class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='PUBLISHED')
    def with_details(self):
        return self.select_related('author', 'category')
    def search(self, query):
        return self.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(excerpt__icontains=query))

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
    title = models.CharField(max_length=200, validators=[nonblank])
    slug = models.SlugField(max_length=220, unique=True, editable=False)
    content = models.TextField(validators=[nonblank])
    excerpt = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts')
    cover_image = models.CharField(max_length=100, choices=COVERS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, editable=False)
    objects = PostQuerySet.as_manager()
    class Meta:
        ordering = ['-published_at', '-created_at', '-pk']
        indexes = [models.Index(fields=['status', '-published_at']), models.Index(fields=['author', '-created_at'])]
        constraints = [models.CheckConstraint(condition=Q(status__in=['DRAFT', 'PUBLISHED']), name='post_valid_status'),
                       models.CheckConstraint(condition=~Q(status='PUBLISHED') | Q(published_at__isnull=False), name='published_has_timestamp')]
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{slugify(self.title)[:180] or "article"}-{uuid.uuid4().hex}'
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)
    @property
    def cover(self):
        return self.cover_image or 'images/technology.svg'
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=2000, validators=[nonblank, MaxLengthValidator(2000)])
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at', 'pk']
        indexes = [models.Index(fields=['post', 'created_at'])]
    def clean(self):
        if self.post_id and self.post.status != Post.Status.PUBLISHED:
            raise ValidationError('Comments are only available on published articles.')
    def __str__(self):
        return self.content[:60]
