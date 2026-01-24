from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from .serializers import (
    StudentDashboardSerializer,
    InstructorDashboardSerializer,
)
from assignments.serializers import AssignmentSerializer


class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, "role") or not user.is_student():
            return Response({"detail": "Access denied. Only students can view this dashboard."}, status=403)

        assignments = Assignment.objects.filter(course__enrollments__student=user).select_related("course")
        submissions = Submission.objects.filter(student=user).select_related("assignment")

        grades_count = submissions.filter(grade__isnull=False).count()
        assignments_count = assignments.count()
        gpa = submissions.filter(grade__isnull=False).aggregate(Avg("grade"))["grade__avg"] or 0
        completion_rate = (submissions.count() / assignments_count * 100) if assignments_count > 0 else 0

        gpa_trend = list(
            submissions.filter(grade__isnull=False).order_by("submitted_at").values("submitted_at", "grade")
        )

        module_completion = assignments.values("module__title").annotate(
            total=Count("id"),
            completed=Count("submissions__student", distinct=True)
        )

        serializer = StudentDashboardSerializer({
            "grades_count": grades_count,
            "assignments_count": assignments_count,
            "gpa": float(gpa),
            "completion_rate": completion_rate,
            "grade_distribution": list(submissions.values("grade").annotate(count=Count("id"))[:10]),
            "gpa_trend": gpa_trend,
            "module_completion": list(module_completion),
        })

        assignments_data = AssignmentSerializer(assignments, many=True).data

        return Response({
            **serializer.data,
            "assignments": assignments_data,
        })


class InstructorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, "role") or not user.is_instructor():
            return Response({"detail": "Access denied. Only instructors can view this dashboard."}, status=403)

        courses = Course.objects.filter(instructor=user).prefetch_related("assignments")
        assignments = Assignment.objects.filter(course__instructor=user).select_related("course")
        submissions = Submission.objects.filter(assignment__course__instructor=user).select_related("assignment")

        courses_taught = courses.count()
        assignments_created = assignments.count()
        submissions_received = submissions.count()
        grades_given = submissions.filter(grade__isnull=False).count()

        course_performance = assignments.values("course__title").annotate(avg_grade=Avg("submissions__grade"))

        performance_trends = list(
            submissions.filter(grade__isnull=False).order_by("submitted_at").values("submitted_at", "grade")
        )

        serializer = InstructorDashboardSerializer({
            "courses_taught": courses_taught,
            "assignments_created": assignments_created,
            "submissions_received": submissions_received,
            "grades_given": grades_given,
            "course_performance": list(course_performance),
            "performance_trends": performance_trends,
        })

        assignments_data = AssignmentSerializer(assignments, many=True).data

        return Response({
            **serializer.data,
            "assignments": assignments_data,
        })


class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # ✅ Role check re‑enabled
        if not hasattr(user, "role") or not user.is_admin():
            return Response(
                {"detail": "Access denied. Only admins can view this dashboard."},
                status=403
            )

        total_courses = Course.objects.count()
        total_students = CustomUser.objects.filter(role="student").count()
        total_instructors = CustomUser.objects.filter(role="instructor").count()
        total_submissions = Submission.objects.count()
        total_grades = Submission.objects.filter(grade__isnull=False).count()
        global_gpa = Submission.objects.filter(grade__isnull=False).aggregate(Avg("grade"))["grade__avg"] or 0

        grade_distribution = Submission.objects.values("grade").annotate(count=Count("id"))[:10]
        enrollment_trends = Enrollment.objects.values("date_enrolled").annotate(count=Count("id"))

        assignments = Assignment.objects.all()
        assignments_data = AssignmentSerializer(assignments, many=True).data

        return Response({
            "total_courses": total_courses,
            "total_students": total_students,
            "total_instructors": total_instructors,
            "total_submissions": total_submissions,
            "total_grades": total_grades,
            "global_gpa": float(global_gpa),
            "grade_distribution": list(grade_distribution),
            "enrollment_trends": list(enrollment_trends),
            "assignments": assignments_data,
        })
