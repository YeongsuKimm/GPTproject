from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone



# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''
        Design and build the login and register user interface
        Implement authentication logic and connect to the backend
        Implement input validation for email, password, and username fields
        Secure user data using password hashing and HTTPS communication
    '''
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    #name = models.CharField(max_length=50, unique=False, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_by_natural_key(self):
        return (self.username,)
    def add_story(self, content, topic=""):
        return Story.objects.create(user=self, content=content, topic=topic)

    def get_stories(self):
        return self.stories.all()  # uses related_name='stories'
    
    def clear_story_history(self):
        """Clears the story history for this user."""
        self.stories.all().delete()

    
class Story(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name="stories")
    topic = models.CharField(max_length=100, blank=True)
    content = models.TextField(default="placeholder content")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

    def get_comment_ids(self):
        return list(self.comments.values_list('id', flat=True))



class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name="comments")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, related_name="comments")
    content = models.TextField(default="placeholder content")
    created_at = models.DateTimeField(default=timezone.now)
