from django.contrib import admin

from .models import FyDataSummary, ReportLog

# Register your models here.
admin.site.register(FyDataSummary)
admin.site.register(ReportLog)
