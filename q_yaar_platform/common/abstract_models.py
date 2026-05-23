"""
Base behaviours. Can be inherited by other models.
"""

from uuid import UUID

from common.constants import Length
from common.uuid import unique_uuid4
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models


class AbstractExternalFacing(models.Model):
    """
    Used by classes to implement uuid as unique field. This is helpful for -
    1. Use external_id as external facing IDs shared with clients. Great as we will not leak information about models
     that would have happened with auto increment integer PK
    2. As FKs when we want to decouple apps into Microservices in future
    """

    external_id = models.UUIDField(default=unique_uuid4, unique=True)

    class Meta:
        abstract = True

    def get_external_id(self, hex=False) -> UUID | str:
        return self.external_id.hex if hex else self.external_id


class AbstractTimeStamped(models.Model):
    """
    Provides created and updated time fields
    """

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class AbstractVersioned(models.Model):
    """
    Implemented by models that require versioning.
    Provides is_deleted and version number fields
    """

    is_deleted = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True


class AbstractUserProfile(models.Model):
    """
    Implemented by specialized profile for base user
    Provides-
    1. OneToOne to platform_user
    2. profile_pic
    """

    # The OneToOneField constraint means, we are expecting the future
    # services to have profile and user in same service and DB
    platform_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="external_id")
    profile_pic = models.JSONField(default=dict)
    profile_name = models.CharField(max_length=Length.USER_NAME, blank=True, null=False)
    is_suspended = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_external_id(self) -> UUID:
        return self.platform_user.external_id

    def get_profile_name(self) -> str:
        return self.profile_name

    def get_phone(self) -> str:
        return self.platform_user.get_phone()

    def get_email(self) -> str:
        return self.platform_user.get_email()

    def get_profile_pic(self):
        return self.profile_pic

    def set_profile_pic(self, profile_pic: dict, save=False):
        self.profile_pic = profile_pic
        if save:
            self.save()
        return self

    def set_profile_name(self, profile_name: str, save=False):
        self.profile_name = profile_name
        if save:
            self.save()
        return self


class AbstractLocationPoint(models.Model):
    """
    Implemented by models that has a location point
    Provides location_pnt field
    """

    location_pnt = gis_models.PointField()

    class Meta:
        abstract = True

    def get_location_point(self):
        return self.location_pnt
    
    def get_location_point_dict(self):
        return {
            "lat": self.location_pnt.y,
            "lng": self.location_pnt.x,
        }
