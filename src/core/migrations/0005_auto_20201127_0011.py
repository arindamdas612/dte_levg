# Generated by Django 3.1.3 on 2020-11-26 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20201126_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='fydatasummary',
            name='filename',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.DeleteModel(
            name='FyData',
        ),
    ]
