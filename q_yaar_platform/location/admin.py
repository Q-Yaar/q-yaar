from django.contrib import admin
from .models import Location, LocationSharingSetting

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'game', 'team', 'lat', 'lon', 'timestamp', 'client')
    list_filter = ('client', 'timestamp')
    readonly_fields = ('player', 'game', 'team', 'lat', 'lon', 'accuracy', 'timestamp', 'client')

@admin.register(LocationSharingSetting)
class LocationSharingSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'is_sharing_enabled', 'tracking_code')
    list_filter = ('is_sharing_enabled',)
