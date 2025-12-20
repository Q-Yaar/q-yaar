import csv

from django.contrib import admin
from django.contrib.gis.db import models
from django.http import HttpResponse
from mapwidgets import GoogleMapPointFieldWidget


class GooglePointFieldWidgetAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField: {"widget": GoogleMapPointFieldWidget}}


class JSONFieldFilter(admin.SimpleListFilter):
    """
    Base JSONFilter class to use by individual attribute filter classes.
    """

    model_json_field_name = None  # name of the json field column in the model
    json_data_property_name = None  # name of one attribute from json data

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        The 1st element in each tuple is the coded value for the option that
        will appear in the URL query.
        The 2nd element is the human-readable name for the option that will appear
        in the right sidebar.
        """
        field_value_set = set()
        model = model_admin.model

        for json_field_data in model.objects.values_list(self.model_json_field_name, flat=True):
            field_value_set.add(self.get_child_value_from_json_field_data(json_field_data))

        return [(v, v) for v in field_value_set]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in
        the query string & retrievable via `self.value()`
        """
        if self.value():
            json_field_query = {f"{self.model_json_field_name}__{self.json_data_property_name}": self.value()}
            return queryset.filter(**json_field_query)
        else:
            return queryset


class ExportCsvMixin:
    """
    Export info in admin table view as a CSV
    """

    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"
