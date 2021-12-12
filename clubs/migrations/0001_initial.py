# Generated by Django 3.2.5 on 2021-12-11 21:09

import clubs.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, max_length=400)),
                ('chess_exp', models.CharField(choices=[('New to chess', 'New To Chess'), ('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Expert', 'Expert')], max_length=12)),
                ('personal_statement', models.CharField(blank=True, max_length=500)),
                ('elo_rating', models.IntegerField(default=1000)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', clubs.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('applicants', models.ManyToManyField(related_name='applicant_of', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='member_of', to=settings.AUTH_USER_MODEL)),
                ('officers', models.ManyToManyField(related_name='officer_of', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_of', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('deadline', models.DateTimeField()),
                ('round', models.IntegerField(default=1)),
                ('group_phase', models.BooleanField(default=False)),
                ('elimination_phase', models.BooleanField(default=True)),
                ('is_final', models.BooleanField(default=False)),
                ('bye', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='has_tournaments', to='clubs.club')),
                ('coorganisers', models.ManyToManyField(blank=True, related_name='coorganises', to=settings.AUTH_USER_MODEL)),
                ('organiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organises', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='participates_in', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournament_wins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pairing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.IntegerField()),
                ('black_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays_black_in', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pairings_within', to='clubs.tournament')),
                ('white_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays_white_in', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_draw', models.BooleanField(blank=True)),
                ('loser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_losses', to=settings.AUTH_USER_MODEL)),
                ('pairing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match', to='clubs.pairing')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_wins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_number', models.IntegerField()),
                ('pairings', models.ManyToManyField(related_name='group_in_which_the_paring_takes_place', to='clubs.Pairing')),
                ('participants', models.ManyToManyField(related_name='participant_in_group', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups_within', to='clubs.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='ClubApplicationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_rejected', models.BooleanField(default=False)),
                ('associated_club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('associated_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
