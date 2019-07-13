from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from datetime import datetime

def get_default_data_dict():
    return {}

def get_default_data_array():
    return []

# DEBATES

class Debate(models.Model):
    title = models.CharField(max_length=255, null=False, unique=True)
    short_title = models.CharField(max_length=255, default="", null=False)
    last_updated = models.DateField(default=datetime.today, null=False)
    total_points = models.IntegerField(default=0, null=False)

    def __str__(self):
        return "{} updated {}".format(self.title, self.last_updated)

class Point(models.Model):
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=False)
    rebuttals = models.ManyToManyField('self', symmetrical=False)

class PointImage(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    url = models.URLField(max_length=255, null=False)
    source = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255, null=True)

class PointHyperlink(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    substring = models.CharField(max_length=255, null=False)
    url = models.URLField(max_length=255, null=False)

# PROGRESS

class Progress(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, default=None, null=False)
    completed_percentage = models.IntegerField(default=0, null=False)
    seen_points = models.ManyToManyField(Point)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.debate.title)

# STARRED

class Starred(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    starred_list = models.ManyToManyField(Debate)

    def buildStarredString(self):
        result = ""
        for debate in self.starred_list.all():
            result += debate.title + ", "

        if result:
            return result[:-2]

    def __str__(self):
        return "{} - {}".format(self.user.username, self.buildStarredString())
