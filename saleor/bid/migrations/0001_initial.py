# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 02:43
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.utils.timezone import utc
import django_prices.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0039_product_start_bid_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BidSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('start_bid', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Start bid time')),
                ('end_bid', models.DateTimeField(default=datetime.datetime(2017, 10, 31, 3, 43, 37, 912424, tzinfo=utc), verbose_name='End bid time')),
                ('products', models.ManyToManyField(to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductBidHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_price', django_prices.models.PriceField(currency='VND', decimal_places=2, max_digits=12, verbose_name='bid price')),
                ('bid_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='bid time')),
                ('user_display_name', models.CharField(blank=True, max_length=255, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bid.BidSession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
