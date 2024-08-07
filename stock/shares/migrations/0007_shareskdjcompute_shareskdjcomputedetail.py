# Generated by Django 4.0 on 2021-12-25 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shares', '0006_sharesban_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharesKdjCompute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intersection_pre_num', models.IntegerField(default=0, help_text='交点前一天')),
                ('intersection_num', models.IntegerField(default=0, help_text='交点')),
                ('intersection_total', models.FloatField(default=0, help_text='交点-总')),
                ('turn_num', models.IntegerField(default=0, help_text='转折点')),
                ('turn_total', models.IntegerField(default=0, help_text='转折点-总')),
                ('shill_type', models.IntegerField(default=0, help_text='技术指标：1.kdj')),
                ('date_as', models.DateField()),
            ],
            options={
                'db_table': 'mc_shares_compute',
            },
        ),
        migrations.CreateModel(
            name='SharesKdjComputeDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy_amount', models.FloatField(default=0, help_text='买点')),
                ('buy_date_as', models.FloatField(default=0, help_text='买点日期')),
                ('buy_amount_end', models.FloatField(default=0, help_text='买点结束')),
                ('buy_date_as_end', models.FloatField(default=0, help_text='买点结束日期')),
                ('shill_type', models.IntegerField(default=0, help_text='技术指标：1.kdj')),
                ('shill_account_type', models.IntegerField(default=0, help_text='具体参考代码注释')),
                ('date_as', models.DateField()),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shares.sharesname')),
            ],
            options={
                'db_table': 'mc_shares_compute_detail',
            },
        ),
    ]
