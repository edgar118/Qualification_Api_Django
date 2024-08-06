from django.shortcuts import render
from rest_framework import viewsets,  permissions
from .serializer import (
    SubjectSerializer, StudentSerializer, 
    ProfessorSerializer, EnrollmentSerializer, 
    ProfessorSerializerForWrite, StudenPerProfesorSerializer, 
    StudentGradeSerializer, GradeSerializer, StudentRegistrationSerializer, UserRegisterSerializer)
from .models import Subject, Student, Professor ,Enrollment
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics

# # Create your views here.

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer

    def get_serializer_class(self):
        if self.action == 'create' or 'update':
            return StudentRegistrationSerializer
        return StudentSerializer
    
    @action(detail=True, methods=['get'])
    def enrolled_subjects(self, request, pk=None):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=404)
        
        enrollments = Enrollment.objects.filter(student=student)
        subjects = [enrollment.subject for enrollment in enrollments]
        serializer = SubjectSerializer(subjects, many=True)
        return Response({'subjects': serializer.data})

    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=404)

        serializer = StudentSerializer(student)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def failed_subjects(self, request, pk=None):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=404)

        serializer = StudentSerializer(student)
        return Response(serializer.data['failed_subjects'])


class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ProfessorSerializerForWrite
        return ProfessorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """
        Retrieve the list of subjects assigned to a professor.
        """
        professor = self.get_object()
        subjects = professor.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def students_per_subject(self, request, pk=None):
        """
        Retrieve the list of students for each subject assigned to a professor.
        """
        professor = self.get_object()
        subjects = professor.subjects.all()
        result = {}
        for subject in subjects:
            enrollments = Enrollment.objects.filter(subject=subject)
            students = [enrollment.student for enrollment in enrollments]
            student_serializer = StudenPerProfesorSerializer(students, many=True)
            result[subject.name] = student_serializer.data

        return Response(result)
    
    @action(detail=True, methods=['get'])
    def student_grades(self, request, pk=None):
        professor = self.get_object()
        subjects = professor.subjects.all()
        result = {}
        for subject in subjects:
            enrollments = Enrollment.objects.filter(subject=subject)
            student_grades = [
                {
                    'student': enrollment.student,
                    'grade': enrollment.grade
                }
                for enrollment in enrollments
            ]
            grade_serializer = StudentGradeSerializer(student_grades, many=True)
            result[subject.name] = grade_serializer.data

        return Response(result)
    
    @action(detail=True, methods=['post'])
    def grade_subject(self, request, pk=None):
        serializer = GradeSerializer(data=request.data)
        if serializer.is_valid():
            subject_id = serializer.validated_data['subject_id']
            grades = serializer.validated_data['grades']
            
            for grade in grades:
                student_id = grade['student_id']
                grade_value = grade['grade']
                enrollment = Enrollment.objects.get(subject_id=subject_id, student_id=student_id)
                enrollment.grade = grade_value
                enrollment.save()
            
            return Response({'status': 'Grades updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    @action(detail=False, methods=['post'])
    def enroll(self, request):
        student_id = request.data.get('student_id')
        subject_ids = request.data.get('subject_ids')
        
        if not student_id or not subject_ids:
            return Response({'error': 'Student ID and Subject IDs are required.'}, status=400)
        
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=404)
        
        subjects = Subject.objects.filter(pk__in=subject_ids)
        
        for subject in subjects:
            prerequisites = subject.prerequisites.all()
            if prerequisites.exists() and not Enrollment.objects.filter(student=student, subject__in=prerequisites).exists():
                return Response({'error': f'El estudiante no cumple con los requisitos previos para {subject.name}.'}, status=400)
            
            student.subjects.add(subject)
        
        return Response({'status': 'Inscription successful.'}, status=201)
    
    @action(detail=True, methods=['put'])
    def update_grade(self, request, pk=None):
        try:
            enrollment = Enrollment.objects.get(pk=pk)
        except Enrollment.DoesNotExist:
            return Response({'error': 'Enrollment not found.'}, status=404)
        
        grade = request.data.get('grade')
        if grade is None:
            return Response({'error': 'Grade is required.'}, status=400)
        
        try:
            grade = float(grade)
        except ValueError:
            return Response({'error': 'Invalid grade value.'}, status=400)
        
        if grade < 0.0 or grade > 5.0:
            return Response({'error': 'Grade must be between 0.0 and 5.0.'}, status=400)
        
        enrollment.grade = grade
        enrollment.save()
        
        serializer = EnrollmentSerializer(enrollment)
        return Response({'status': 'Grade updated successfully.', 'data': serializer.data}, status=200)
    
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]