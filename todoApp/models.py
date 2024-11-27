from django.db import models
from django.core.exceptions import ValidationError
import datetime

class Todo(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("WORKING", "Working"),
        ("COMPLETED", "Completed"),
        ("PENDING REVIEW", "PENDING REVIEW"),
        ("OVERDUE", "OVERDUE"),
        ("CANCELLED", "CANCELLED"),
    ]
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=1000, blank=False)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    tags = models.ManyToManyField("Tag", related_name="todos")
    def clean(self):
        super().clean()
        if self.due_date < datetime.date.today():
            raise ValidationError({'due_date': "Due date cannot be in the past."})
        
    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # todo field removed to avoid circular reference
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    def __str__(self):
        return self.name
