# Generated by Django 5.1.2 on 2024-11-21 00:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_examenes', '0009_alter_examen_planificacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='opcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=255, verbose_name='Texto de la opción')),
                ('es_correcta', models.BooleanField(default=False, verbose_name='Es la opción correcta')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opciones', to='gestion_examenes.pregunta')),
            ],
        ),
    ]
