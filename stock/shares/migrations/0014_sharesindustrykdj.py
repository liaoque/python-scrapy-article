# Generated by Django 4.0 on 2022-01-13 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shares', '0013_sharesindustry'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharesIndustryKdj',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('k', models.FloatField(default=0)),
                ('d', models.FloatField(default=0)),
                ('j', models.FloatField(default=0)),
                ('cycle_type', models.IntegerField(default=0, help_text='1.9,3,3')),
                ('date_as', models.DateField()),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shares.sharesname')),
            ],
            options={
                'db_table': 'mc_shares_industry_kdj',
            },
        ),
    ]