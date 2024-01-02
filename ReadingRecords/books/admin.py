from django.contrib import admin
from .models import Developer
from .models import BookRecord, Friend, Group, Good
# Register your models here.

admin.site.register(Developer)
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Good)