# Generated by Django 4.0 on 2022-02-13 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shares', '0016_alter_sharesmacd_cycle_type'),
        ('polls', '0002_shares_sharesname'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharesKdjCompute',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('shares.shareskdjcompute',),
        ),
        migrations.CreateModel(
            name='SharesKdjComputeDetail',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('shares.shareskdjcomputedetail',),
        ),
    ]