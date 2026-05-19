from django.db import models

# Create your models here.
class UserPrediction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_input = models.JSONField()  # Stores user inputs as a JSON object
    predicted_price = models.FloatField()

    def __str__(self):
        return f"Prediction at {self.timestamp}: {self.predicted_price}"