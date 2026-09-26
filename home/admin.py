from django.contrib import admin

from .models import Aadhar_Details, State


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
	list_display = ["name"]
	search_fields = ["name"]


@admin.register(Aadhar_Details)
class AadharDetailsAdmin(admin.ModelAdmin):
	list_display = ["number", "First_name", "Last_name", "Phone_number", "state"]
	search_fields = ["number", "First_name", "Last_name", "Phone_number"]
	list_filter = ["gender", "state"]
