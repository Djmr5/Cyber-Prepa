from django.contrib import admin
from .models import Student, Play, Game, Sanction

# Register your models here.
admin.site.register(Student)
admin.site.register(Play)
admin.site.register(Game)
admin.site.register(Sanction)
