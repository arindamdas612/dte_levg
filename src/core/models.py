from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class FyDataSummary(models.Model):
    year = models.IntegerField()
    period = models.IntegerField()
    no_of_records = models.IntegerField(default=0)
    total_fte = models.DecimalField(
        max_digits=20, decimal_places=10, default=0.0)
    filename = models.CharField(max_length=25, null=True, blank=True)
    create_ts = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        formatted_time = timezone.localtime(self.create_ts)
        return f"FY{str(self.year)[2:]}P{self.period} by {self.created_by.get_full_name()} on {formatted_time}"

    def display_filename(self):
        return self.filename.split('.')[0]

    def display_filetag(self):
        return self.filename.split('.')[0].split('_')[0]


class ReportLog(models.Model):
    view_ts = models.DateTimeField(auto_now_add=True)
    viewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
