"""
Database Models
"""
from unittest.util import _MAX_LENGTH
from django.conf import settings
from multiprocessing.sharedctypes import Value
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

class UserManager(BaseUserManager):
    """Manager for the users """
    def create_user(self, email, password= None, **extra_fields):
        """create , save and return a new user """
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email= self.normalize_email(email), password= None, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """create and return a super user"""
        user = self.create_user(email, password) # call above general method and add belowparameters to make it super user
        user.is_staff = True
        user.is_superuser = True
        user.save(using= self._db)

        return user


class User(AbstractBaseUser,PermissionsMixin):
    """User in the system """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description= models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length=255,blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title # id we dont specify this it will return just ID of the Recipe , when we call str(Recipe)

class Tag(models.Model):
    """Tag object"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name