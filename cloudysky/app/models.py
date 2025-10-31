from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class ModerationReason(models.Model):
    reason_text = models.CharField(max_length=255)

    def __str__(self):
        return self.reason_text

class UserProfile(models.Model):
    USER_ROLES = [
        ('serf', 'Serf'),
        ('admin', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='serf')
    bio = models.TextField(blank=True, null=True)

class Avatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='avatars/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    hidden_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hidden_posts')
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_reason = models.ForeignKey(ModerationReason, on_delete=models.SET_NULL, null=True, blank=True)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    hidden_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hidden_comments')
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_reason = models.ForeignKey(ModerationReason, on_delete=models.SET_NULL, null=True, blank=True)

class Media(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='media_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
