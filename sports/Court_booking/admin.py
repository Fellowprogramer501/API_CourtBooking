from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from . import models
class view_branch(admin.ModelAdmin):
    list_display = ['Location', 'contact_num']
    filter_horizontal = ['Sports']

class BranchImageInline(admin.TabularInline): 
    model = models.court_pictures
    extra = 3

class view_sport(admin.ModelAdmin):
    list_display = ['branch', 'sport','Code', 'user']

class view_courts(admin.ModelAdmin):
    list_display = ['sport','branch','courts','available_courts']
    inlines = [BranchImageInline]

admin.site.register(models.court_pictures)
admin.site.register(models.booking_order, view_sport)
admin.site.register(models.Branch, view_branch)
admin.site.register(models.Court,view_courts)
admin.site.register(models.Sport)

