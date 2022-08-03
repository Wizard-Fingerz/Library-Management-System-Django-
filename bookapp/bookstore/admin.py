from django.contrib import admin
from .models import User, Book, Chat, DeleteRequest, Feedback

# Register your models here.
admin.site.register([User, Book, Chat, DeleteRequest, Feedback])