# models.py
from django.db import models

class ProjectElement(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=100)
    project_element = models.ForeignKey(ProjectElement, related_name='materials', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
