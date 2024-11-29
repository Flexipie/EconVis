from django.db import models


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
