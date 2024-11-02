# models.py
from django.db import models
from django.contrib.auth.models import User

class ProjectElement(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=100)
    project_element = models.ForeignKey(ProjectElement, related_name='materials', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class QuotationRequest(models.Model):
    project_element = models.ForeignKey(ProjectElement, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")  # Status field

    def __str__(self):
        return f"Request by {self.user} for {self.project_element}"
