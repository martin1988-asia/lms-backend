from django.db import models
from assignments.models import Assignment

class Grade(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="grades")
    score = models.IntegerField()
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.assignment.title} - {self.score}"
