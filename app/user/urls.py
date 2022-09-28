"""url mappingd for the user api
"""
from django.urls import path
from user import views

app_name = 'user' # if u see test_user_api.py reverse('user:create')

urlpatterns = [
    path('create/',views.CreateUserView.as_view(),name='create') # see above
]