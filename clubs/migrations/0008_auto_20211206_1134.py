# Generated by Django 3.2.5 on 2021-12-06 11:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0007_merge_0006_match_tournament_0006_user_elo_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='applicants',
            field=models.ManyToManyField(related_name='applicant_of', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='club',
            name='members',
            field=models.ManyToManyField(related_name='member_of', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='club',
            name='officers',
            field=models.ManyToManyField(related_name='officer_of', to=settings.AUTH_USER_MODEL),
        ),
    ]
