from django.contrib import admin
from .models import Flowers,Favorits,Cart,Category,Subcategory
# Register your models here.
admin.site.register(Flowers)
admin.site.register(Favorits)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(Subcategory)

