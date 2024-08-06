from rest_framework import serializers
from .models import Subject, Student, Professor ,Enrollment
from django.contrib.auth.models import User

class SubjectSerializer(serializers.ModelSerializer):
    prerequisites = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True, required=False, allow_null=True)
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'prerequisites']
        extra_kwargs = {
            'first_name': {'help_text': 'First name of the student'},
            'last_name': {'help_text': 'Last name of the student'},
            'email': {'help_text': 'Email address of the student'},
        }

class StudentRegistrationSerializer(serializers.ModelSerializer):
    subject_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Student
        fields = ['first_name','last_name', 'email','date_of_birth','enrollment_date', 'subject_ids']

    def create(self, validated_data):
        subject_ids = validated_data.pop('subject_ids', [])
        student = Student.objects.create(**validated_data)

        subjects = Subject.objects.filter(pk__in=subject_ids)
        for subject in subjects:
            prerequisites = subject.prerequisites.all()
            if prerequisites.exists():
                approved_subjects = student.approved_subjects()
                if not all(prerequisite in approved_subjects for prerequisite in prerequisites):
                    raise serializers.ValidationError({
                        'subject_ids': [f'El estudiante no cumple con los requisitos previos para {subject.name}.']
                    })
            Enrollment.objects.create(student=student, subject=subject)

        return student
    
class StudentSerializer(serializers.ModelSerializer):
    approved_subjects = serializers.SerializerMethodField()
    average_grade = serializers.SerializerMethodField()
    failed_subjects = serializers.SerializerMethodField()
    enrollments = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email', 'date_of_birth', 'enrollment_date',
                'approved_subjects', 'average_grade', 'failed_subjects', 'enrollments']

    def get_enrollments(self, obj):
        enrollments = Enrollment.objects.filter(student=obj)
        return EnrollmentSerializer(enrollments, many=True).data
    
    
    def get_approved_subjects(self, obj):
        subjects = obj.approved_subjects()
        return SubjectSerializer(subjects, many=True).data

    def get_average_grade(self, obj):
        return obj.average_grade()
    
    def get_failed_subjects(self, obj):
        subjects = obj.failed_subjects()
        return SubjectSerializer(subjects, many=True).data
    

class StudenPerProfesorSerializer(serializers.ModelSerializer):
    extra_kwargs = {
            'first_name': {'help_text': 'First name of the student'},
            'last_name': {'help_text': 'Last name of the student'},
            'email': {'help_text': 'Email address of the student'},
        }
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email']

class StudentGradeSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    grade = serializers.FloatField()

class GradeSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField()
    grades = serializers.ListField(
        child=serializers.DictField(child=serializers.FloatField())
    )
    
    def validate(self, data):
        subject_id = data.get('subject_id')
        grades = data.get('grades')

        if not Subject.objects.filter(pk=subject_id).exists():
            raise serializers.ValidationError({"subject_id": "Materia no encontrada."})

        for grade in grades:
            student_id = grade.get('student_id')
            if not Enrollment.objects.filter(subject_id=subject_id, student_id=student_id).exists():
                raise serializers.ValidationError({"grades": f"Inscripción no encontrada para el estudiante con ID {student_id}."})

        return data

class ProfessorSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Professor
        fields = ['id', 'first_name', 'last_name', 'email', 'department', 'subjects']

class ProfessorSerializerForWrite(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True, write_only=True)

    class Meta:
        model = Professor
        fields = ['id', 'first_name', 'last_name', 'email', 'department', 'subjects']

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'subject', 'enrollment_date', 'grade', 'is_passed']
        read_only_fields = ['is_passed']

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user