# Generated by Django 4.2.1 on 2023-07-21 21:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('displayName', models.CharField(max_length=100)),
                ('available', models.BooleanField(default=True)),
                ('show', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ended', models.BooleanField(default=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('week', models.IntegerField()),
                ('year', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rental.game')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.CharField(max_length=9, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('hash', models.CharField(max_length=1000)),
                ('sanctioned', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sanction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.CharField(max_length=255)),
                ('play', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rental.plays')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rental.student')),
            ],
        ),
        migrations.AddField(
            model_name='plays',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rental.student'),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actionPerformed', models.CharField(max_length=255)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
