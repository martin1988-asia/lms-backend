from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.models import CustomUser
from courses.models import Course, Module
from assignments.models import Assignment, Submission

from .serializers import (
    UserSerializer,
    CourseSerializer,
    ModuleSerializer,
    AssignmentSerializer,
    SubmissionSerializer,
)
from accounts.serializers import RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "role") and user.role == "admin":
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role") or user.role != "admin":
            return Response(
                {"detail": "Access denied. Only admins can create users here. Use /auth/signup for registration."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "instructor":
            return Course.objects.filter(instructor=user)
        elif user.role == "student":
            return Course.objects.filter(enrollments__student=user)
        elif user.role == "admin":
            return Course.objects.all()
        return Course.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)   # ✅ always return array
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ["instructor", "admin"]:
            return Response(
                {"detail": "Access denied. Only instructors or admins can create courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role not in ["instructor", "admin"]:
            return Response(
                {"detail": "Access denied. Only instructors or admins can create modules."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "instructor":
            return Assignment.objects.filter(course__instructor=user)
        elif user.role == "student":
            return Assignment.objects.filter(course__enrollments__student=user)
        elif user.role == "admin":
            return Assignment.objects.all()
        return Assignment.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)   # ✅ always return array
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "instructor":
            return Response(
                {"detail": "Access denied. Only instructors can create assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            return Submission.objects.filter(student=user)
        elif user.role == "instructor":
            return Submission.objects.filter(assignment__course__instructor=user)
        elif user.role == "admin":
            return Submission.objects.all()
        return Submission.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "student":
            return Response(
                {"detail": "Access denied. Only students can submit assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            RegisterSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
