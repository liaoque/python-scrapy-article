# Generated by Django 4.0 on 2021-12-27 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shares', '0007_shareskdjcompute_shareskdjcomputedetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareskdjcompute',
            name='intersection_pre_total_amount',
            field=models.FloatField(default=0, help_text='交点前一天-总盈利'),
        ),
        migrations.AddField(
            model_name='shareskdjcompute',
            name='intersection_total_amount',
            field=models.FloatField(default=0, help_text='交点-总盈利'),
        ),
        migrations.AddField(
            model_name='shareskdjcompute',
            name='turn_total_amount',
            field=models.FloatField(default=0, help_text='转折点-总盈利'),
        ),
        migrations.AlterField(
            model_name='shareskdjcompute',
            name='intersection_total',
            field=models.IntegerField(default=0, help_text='交点-总'),
        ),
    ]