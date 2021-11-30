from django.db import models
from django.utils import timezone


class Country(models.Model):
    code_2 = models.CharField(max_length=100, null=True, blank=True)
    code_3 = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)


class PingData(models.Model):
    lat = models.CharField(max_length=20, null=True, blank=True)
    long = models.CharField(max_length=20, null=True, blank=True)
    connection_type = models.CharField(max_length=20, null=True, blank=True)
    ping_time = models.CharField(max_length=20, null=True, blank=True)
    web_link = models.TextField(blank=True, null=True)
    network = models.CharField(max_length=100, null=True, blank=True)
    test_time = models.DateTimeField(blank=True, null=True)
    provider = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class MasterData(models.Model):
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    national = models.FloatField(max_length=1000, blank=True, null=True)
    intra = models.FloatField(max_length=1000, blank=True, null=True)
    extra = models.FloatField(max_length=1000, blank=True, null=True)
    data_gb_per_month = models.FloatField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class InternetDataFlow(models.Model):
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    gb_per_sec = models.FloatField(max_length=1000, blank=True, null=True)
    at_time = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class DataFlowMatrixCountry(models.Model):
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)


class DataFlowMatrix(models.Model):
    from_country = models.ForeignKey(DataFlowMatrixCountry, blank=True, null=True, on_delete=models.CASCADE)
    data_gb_per_month = models.FloatField(max_length=1000, blank=True, null=True)
    to_country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)


