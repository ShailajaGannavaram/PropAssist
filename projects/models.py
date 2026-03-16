from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    developer = models.CharField(max_length=200)
    total_units = models.IntegerField(default=0)
    handover_date = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    exterior_video_url = models.URLField(blank=True)
    interior_video_url = models.URLField(blank=True)
    story_video_url = models.URLField(blank=True)
    highlight_video_url = models.URLField(blank=True)
    brochure_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UnitType(models.Model):
    UNIT_CHOICES = [
        ('studio', 'Studio'),
        ('1br', '1 Bedroom'),
        ('2br', '2 Bedrooms'),
        ('3br', '3 Bedrooms'),
        ('penthouse', 'Penthouse'),
        ('villa', 'Villa'),
        ('mansion', 'Mansion'),
        ('retail', 'Retail'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='unit_types')
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES)
    total_units_available = models.IntegerField(default=0)
    area_sqft_min = models.FloatField(default=0)
    area_sqft_max = models.FloatField(default=0)
    starting_price_aed = models.FloatField(default=0)
    floor_plan_image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.project.name} - {self.unit_type}"


class RoomDetail(models.Model):
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE, related_name='rooms')
    room_name = models.CharField(max_length=100)
    area_sqft = models.FloatField(default=0)
    area_sqm = models.FloatField(default=0)

    def __str__(self):
        return f"{self.unit_type} - {self.room_name}"


class Amenity(models.Model):
    CATEGORY_CHOICES = [
        ('recreation', 'Recreation'),
        ('kids', 'Kids'),
        ('wellness', 'Wellness'),
        ('social', 'Social'),
        ('retail', 'Retail'),
        ('other', 'Other'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class PaymentPlan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payment_plans')
    plan_name = models.CharField(max_length=200, default='Standard Payment Plan')
    installment_number = models.IntegerField()
    percentage = models.FloatField()
    due_when = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.name} - Installment {self.installment_number}"


class ProjectImage(models.Model):
    CATEGORY_CHOICES = [
        ('interior', 'Interior'),
        ('exterior', 'Exterior'),
        ('lobby', 'Lobby'),
        ('gym', 'Gym'),
        ('pool', 'Pool'),
        ('villa', 'Villa'),
        ('penthouse', 'Penthouse'),
        ('other', 'Other'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    unit_type = models.CharField(max_length=50, blank=True)
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.project.name} - {self.category}"


class NearbyPlace(models.Model):
    PLACE_TYPE_CHOICES = [
        ('airport', 'Airport'),
        ('mall', 'Mall'),
        ('hospital', 'Hospital'),
        ('beach', 'Beach'),
        ('school', 'School'),
        ('restaurant', 'Restaurant'),
        ('other', 'Other'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='nearby_places')
    place_name = models.CharField(max_length=200)
    place_type = models.CharField(max_length=20, choices=PLACE_TYPE_CHOICES, default='other')
    distance_km = models.FloatField(default=0)
    travel_time_minutes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.project.name} - {self.place_name}"


class FloorPlan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='floor_plans')
    floor_number = models.CharField(max_length=50)
    floor_plan_image_url = models.URLField(blank=True)
    units_on_floor = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.project.name} - Floor {self.floor_number}"
