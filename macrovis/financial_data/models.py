from django.db import models
from django.contrib.auth.models import User


class Country(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'countries'


class Indicator(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FinancialData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    year = models.IntegerField()
    value = models.FloatField(null=True)

    class Meta:
        unique_together = ('country', 'indicator', 'year')

    def __str__(self):
        return f"{self.country.name} - {self.indicator.name} ({self.year})"


# Create your models here.

class FavoriteComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country1 = models.CharField(max_length=100)  # Store the name or code of the country
    country2 = models.CharField(max_length=100)
    index = models.CharField(max_length=100)  # The index being analyzed (e.g., GDP)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.country1} vs {self.country2} -- ({self.index})"
    

class LastSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country1 = models.CharField(max_length=100)
    country2 = models.CharField(max_length=100)
    indicator = models.CharField(max_length=50)  # Stores the indicator code
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest first
    
    def __str__(self):
        try:
            indicator = Indicator.objects.get(code=self.indicator)
            indicator_name = indicator.name
        except Indicator.DoesNotExist:
            indicator_name = self.indicator
        return f"{self.country1} vs {self.country2} -- {indicator_name} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
