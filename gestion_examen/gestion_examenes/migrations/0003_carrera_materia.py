# Generated by Django 5.1.2 on 2024-11-03 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_examenes', '0002_semestre'),
    ]

    operations = [
        migrations.CreateModel(
            name='carrera',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre de la carrera')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('modalidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_examenes.modalidad')),
                ('semestre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_examenes.semestre')),
            ],
        ),
        migrations.CreateModel(
            name='materia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre de la materia')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('carrera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_examenes.carrera')),
            ],
        ),
    ]
