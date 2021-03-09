# Generated by Django 3.1.7 on 2021-02-27 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xwareBackend', '0010_auto_20210226_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='result',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.CreateModel(
            name='eventImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(default='', max_length=200)),
                ('type', models.CharField(default='', max_length=200)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='xwareBackend.event')),
            ],
        ),
    ]
