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
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Markup field
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class QuotationRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved by Admin", "Approved by Admin"),
        ("Declined by Admin", "Declined by Admin"),
        ("Declined by User", "Declined by User"),
        ("Complete", "Complete"),
        ("Approved by User", "Approved by User"),
    ]

    project_element = models.ManyToManyField(ProjectElement)  # Many-to-Many relationship
    material = models.ManyToManyField(Material, blank=True)  # Many-to-Many relationship with Material
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")  # Updated status field
    quantity = models.PositiveIntegerField(default=1)  # Quantity field
    area_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Area size in sqm or sq ft
    location = models.CharField(max_length=255, null=True, blank=True)  # Location of the project

    def __str__(self):
        # Join the names of the related ProjectElements for better readability
        elements = ", ".join(str(pe) for pe in self.project_element.all())
        return f"Request by {self.user} for {elements or 'no elements'}"
