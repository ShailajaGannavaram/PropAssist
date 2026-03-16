from django.contrib import admin
from .models import Project, UnitType, RoomDetail, Amenity, PaymentPlan, ProjectImage, NearbyPlace, FloorPlan


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'developer', 'total_units', 'handover_date']
    search_fields = ['name', 'location', 'developer']


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ['project', 'unit_type', 'total_units_available', 'area_sqft_min', 'area_sqft_max', 'starting_price_aed']
    list_filter = ['project', 'unit_type']


@admin.register(RoomDetail)
class RoomDetailAdmin(admin.ModelAdmin):
    list_display = ['unit_type', 'room_name', 'area_sqft', 'area_sqm']
    list_filter = ['unit_type__project']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'category']
    list_filter = ['project', 'category']


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['project', 'plan_name', 'installment_number', 'percentage', 'due_when']
    list_filter = ['project']


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'category', 'unit_type', 'caption']
    list_filter = ['project', 'category']


@admin.register(NearbyPlace)
class NearbyPlaceAdmin(admin.ModelAdmin):
    list_display = ['project', 'place_name', 'place_type', 'distance_km', 'travel_time_minutes']
    list_filter = ['project', 'place_type']


@admin.register(FloorPlan)
class FloorPlanAdmin(admin.ModelAdmin):
    list_display = ['project', 'floor_number', 'units_on_floor']
    list_filter = ['project']
