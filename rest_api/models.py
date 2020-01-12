from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from django.core.validators import URLValidator
from django.utils import timezone
from .utils.constants import *

# DEBATES

class Debate(models.Model):
    title = models.CharField(max_length=255, null=False, unique=True)
    short_title = models.CharField(max_length=255, null=False)
    tags = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now, null=False)
    total_points = models.PositiveIntegerField(default=0, null=False, blank=False)
    all_points_primary_keys = ArrayField(models.PositiveIntegerField(default=0, null=False, blank=False), default=list, null=False, blank=False)

class Point(models.Model):
    # Optional because only root points should reference debate directly
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, null=True, blank=True)
    side = models.CharField(max_length=255, choices=[(pro_value, ""), (con_value, ""), (context_value, "")], null=False)
    short_description = models.TextField(null=False)
    description = models.TextField(null=False)
    rebuttals = models.ManyToManyField('self', symmetrical=False, blank=True)
    time_added = models.DateTimeField(default=timezone.now, blank=True)

    def get_all_points(self):
        all_points = [self]
        for rebuttal in self.rebuttals.all(): all_points += rebuttal.get_all_points()
        return all_points

    class Meta:
        unique_together = (short_description_key, description_key,)

class PointHyperlink(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    substring = models.TextField(null=False)
    url = models.TextField(null=False, validators=[URLValidator()])

# PROGRESS

class Progress(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, default=None, null=False)
    seen_points = models.ManyToManyField(Point)

# STARRED

class Starred(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    starred_list = models.ManyToManyField(Debate)
