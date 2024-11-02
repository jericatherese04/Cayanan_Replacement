# models.py
from django.db import models
from django.contrib.auth.models import User


class ProjectElement(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=200)
    project_element = models.ForeignKey(ProjectElement, related_name='materials', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Add markup field
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return self.name


class QuotationRequest(models.Model):
    project_element = models.ForeignKey(ProjectElement, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")  # Status field
    quantity = models.PositiveIntegerField(default=1)  # Quantity field
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Area size in sqm or sq ft
    location = models.CharField(max_length=255, null=True, blank=True)  # Location of the project

    def __str__(self):
        return f"Request by {self.user} for {self.project_element}"
