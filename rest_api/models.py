from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

class Debate(models.Model):
    # debate title
    title = models.CharField(max_length=255, null=False, unique=True)
    # debate subtitle
    subtitle = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)

def get_default_data_array():
    return []

class Progress(models.Model):
    # settings.AUTH_USER_MODEL uses User from django.contrib.auth.models unless you define a custom user in the future
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=False) # always needs to be authenticated to make this post request

    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, default=None, null=False)
    completed = models.BooleanField(default=False)
    seen_points = ArrayField(models.CharField(max_length=255, null=False), default=get_default_data_array, null=False)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.debate.title)

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
