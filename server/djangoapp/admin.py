from django.contrib import admin
from .models import CarMake, CarModel

# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 2

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name','type','year')
    list_filter = ['year']
    search_fields = ['name','type']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name','country','description')
    inlines = [CarModelInline]

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
