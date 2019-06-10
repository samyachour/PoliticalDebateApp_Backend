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
    # debate title
    title = models.CharField(max_length=255, null=False, unique=True)
    # debate subtitle
    last_updated = models.DateField(default=datetime.today, null=False)
    total_points = models.IntegerField(default=0, null=False)
    debate_map = JSONField(default=get_default_data_dict, null=False)

    def __str__(self):
        return "{} updated {}".format(self.title, self.last_updated)

# PROGRESS

class Progress(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, default=None, null=False)
    completed = models.BooleanField(default=False)
    seen_points = ArrayField(models.CharField(max_length=255, null=False), default=get_default_data_array, null=False)

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
