""" to avoid below flake erors we use # noqa beside import  
 ./core/admin.py:1:1: F401 'django.contrib.admin' imported but unused
"""

from django.contrib import admin  # noqa

# Register your models here.
