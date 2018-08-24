from django.db import models


#: Length of CharFields used to hold the names of objects
MAX_LENGTH_NAME = 63


class BaseAppDataModel(models.Model):
    #: Friendly name of this application
    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            blank=False, null=False)

    #: A brief description
    description = models.TextField(blank=True, null=False)

    #: Address at which the API may be accessed
    url = models.URLField(blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
