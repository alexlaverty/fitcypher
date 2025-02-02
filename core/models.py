from django.db import models
from django.contrib.auth.models import User

class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entries")
    date = models.DateTimeField()
    tracking = models.CharField(max_length=255)
    string_value = models.CharField(max_length=255, null=True, blank=True)
    numerical_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    source = models.TextField(null=True, blank=True, default="fitcypher")

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')}, {self.user}, {self.string_value}"