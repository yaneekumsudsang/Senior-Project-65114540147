from django.contrib import admin
from django.contrib import admin
from .models import Member, Store
import Koupon
from .models import *

# Register your models here.
admin.site.register(Promotion)
admin.site.register(Member)
admin.site.register(Store)