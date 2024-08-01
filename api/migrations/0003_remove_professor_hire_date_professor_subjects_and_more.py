# Generated by Django 5.0.7 on 2024-07-31 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_enrollment_professor_student_subject_delete_course_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professor',
            name='hire_date',
        ),
        migrations.AddField(
            model_name='professor',
            name='subjects',
            field=models.ManyToManyField(related_name='professors', to='api.subject'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='prerequisites',
            field=models.ManyToManyField(blank=True, related_name='required_for', to='api.subject'),
        ),
    ]
