from django.contrib import admin

from .models import Workout, Post, Commenter, Comment

admin.site.register(Workout)
admin.site.register(Post)
admin.site.register(Commenter)
admin.site.register(Comment)
