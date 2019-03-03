from django.db import models

class Debates(models.Model):
    # debate title
    title = models.CharField(max_length=255, null=False)
    # debate subtitle
    subtitle = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)

class Progress(models.Model):
    # User ID
    user_ID = models.IntegerField(null=False)
    # debate title
    debate_title = models.CharField(max_length=255, null=False)
    # debate point seen
    debate_point = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {} - {}".format(self.user_ID, self.debate_title, self.debate_point)
