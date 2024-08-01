from django.db import models

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='required_for', blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    enrollment_date = models.DateField(auto_now_add=True)

    def approved_subjects(self):
        enrollments = Enrollment.objects.filter(student=self, grade__gte=3.0)
        return [enrollment.subject for enrollment in enrollments]

    def average_grade(self):
        enrollments = Enrollment.objects.filter(student=self)
        if not enrollments:
            return None
        grades = [enrollment.grade for enrollment in enrollments if enrollment.grade is not None]
        if not grades:
            return None
        return sum(grades) / len(grades)
    
    def failed_subjects(self):
        enrollments = Enrollment.objects.filter(student=self, grade__lt=3.0)
        return [enrollment.subject for enrollment in enrollments]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Professor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    subjects = models.ManyToManyField('Subject', related_name='professors')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)

    def is_passed(self):
        return self.grade is not None and self.grade >= 3.0

    def __str__(self):
        return f"{self.student} - {self.subject}"