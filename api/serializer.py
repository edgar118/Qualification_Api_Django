from rest_framework import serializers
from .models import Subject, Student, Professor ,Enrollment

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']
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
            if not prerequisites.exists() or Enrollment.objects.filter(student=student, subject__in=prerequisites).exists():
                Enrollment.objects.create(student=student, subject=subject)
            else:
                raise serializers.ValidationError({
                    'subject_ids': [f'El estudiante no cumple con los requisitos previos para {subject.name}.']
                })
        
        return student
    
class StudentSerializer(serializers.ModelSerializer):
    approved_subjects = serializers.SerializerMethodField()
    average_grade = serializers.SerializerMethodField()
    failed_subjects = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email', 'date_of_birth', 'enrollment_date',
                'approved_subjects', 'average_grade', 'failed_subjects']

    def create(self, validated_data):
        subject_ids = validated_data.pop('subject_ids', [])
        student = Student.objects.create(**validated_data)
        
        subjects = Subject.objects.filter(pk__in=subject_ids)
        for subject in subjects:
            prerequisites = subject.prerequisites.all()
            if not prerequisites.exists() or Enrollment.objects.filter(student=student, subject__in=prerequisites).exists():
                Enrollment.objects.create(student=student, subject=subject)
            else:
                raise serializers.ValidationError({
                    'subject_ids': [f'El estudiante no cumple con los requisitos previos para {subject.name}.']
                })
        
        return student
    
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