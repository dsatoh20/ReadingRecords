from django.contrib import admin
from .models import Developer
from .models import BookRecord, Friend, Group, Good, Chat
# Register your models here.

admin.site.register(Developer)
admin.site.register(BookRecord)
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Good)
admin.site.register(Chat)