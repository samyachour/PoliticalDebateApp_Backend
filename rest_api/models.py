from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

class Debates(models.Model):
    # debate title
    title = models.CharField(max_length=255, null=False)
    # debate subtitle
    subtitle = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)

def get_default_data_array():
    return []

class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None) # always needs to be authenticated to make this post request
    debate_title = models.CharField(max_length=255, null=False)
    seen_points = ArrayField(models.CharField(max_length=255, null=False), default=get_default_data_array)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.debate_title)
