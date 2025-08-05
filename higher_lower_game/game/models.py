from django.db import models

# Create your models here.

class ClassicItem(models.Model):
    name = models.CharField(max_length=100)
    monthly_searches = models.IntegerField()
    image = models.ImageField(upload_to='classic_images/', blank=True, null=True)

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

class ClassicLeaderboard(models.Model):
    nickname = models.CharField(max_length=50)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.nickname}: {self.score}"

class CSLeaderboard(models.Model):
    nickname = models.CharField(max_length=50)
    score = models.IntegerField()
    difficulty = models.CharField(max_length=10, default='easy')  # 'easy', 'medium', 'hard'

    def __str__(self):
        return f"{self.nickname}: {self.score}"