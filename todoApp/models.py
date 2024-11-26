from django.db import models


class Todo(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('WORKING', 'Working'),
        ('COMPLETED', 'Completed'),
        ('PENDING REVIEW', 'PENDING REVIEW'),
        ('OVERDUE', 'OVERDUE'),
        ('CANCELLED', 'CANCELLED')
    ]
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=1000, blank=False)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    # I want to store unique tags for each To-Do item and I am passing a list like ['tag1', 'tag2']
    tags = models.JSONField(default=list)

    def __str__(self):
        return self.title
