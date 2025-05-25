from django.db import models

# Create your models here.

class ClassicItem(models.Model):
    name = models.CharField(max_length=100)
    monthly_searches = models.IntegerField()

    def __str__(self):
        return self.name

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

class CSQuestion(models.Model):
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=50)  # spremamo broj kao string
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return self.question_text

