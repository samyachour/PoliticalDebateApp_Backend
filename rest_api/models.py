from django.db import models

class Debates(models.Model):
    # debate title
    title = models.CharField(max_length=255, null=False)
    # debate subtitle
    subtitle = models.CharField(max_length=255, null=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.subtitle)
