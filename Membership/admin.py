from django.contrib import admin
from .models import *

admin.site.register(Membership)
admin.site.register(Subscription)
admin.site.register(UserMembership)