# Generated by Django 3.0.6 on 2020-05-14 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candlestick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(db_index=True, unique=True)),
                ('open', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
                ('volume_btc', models.FloatField()),
                ('volume_currency', models.FloatField()),
                ('weighted_price', models.FloatField()),
            ],
        ),
    ]
