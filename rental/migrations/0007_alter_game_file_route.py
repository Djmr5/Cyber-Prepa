# Generated by Django 4.2.1 on 2023-09-26 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0006_game_file_route_alter_sanction_play'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='file_route',
            field=models.CharField(default='assets/games_cards/game.png', max_length=255),
        ),
    ]
