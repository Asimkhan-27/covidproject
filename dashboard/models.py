from django.db import models

class DummyModel(models.Model):
    name = models.CharField(max_length=100, default='Dashboard Generator')

    def __str__(self):
        return self.name


class ChartTrigger(models.Model):
    name = models.CharField(max_length=100, default="Generate Charts")

    def __str__(self):
        return self.name