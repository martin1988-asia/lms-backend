from django.db.models import Avg, Count, F
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import RolePermission
from accounts.models import CustomUser
from courses.models import Course
from enrollments.models import Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade

from .serializers import (
    StudentAnalyticsSerializer,
    InstructorAnalyticsSerializer,
    AdminAnalyticsSerializer,
)


class IsStudent(RolePermission):
    allowed_roles = ["student"]


class IsInstructor(RolePermission):
    allowed_roles = ["instructor"]


class IsAdmin(RolePermission):
    allowed_roles = ["admin"]


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        if hasattr(user, "role") and user.role == "student":
            return self.student_analytics(user)
        if hasattr(user, "role") and user.role == "instructor":
            return self.instructor_analytics(user)
        if (hasattr(user, "role") and user.role == "admin") or user.is_staff or user.is_superuser:
            return self.admin_analytics()
        return Response({"detail": "No analytics available for this role."})

    # --- Student analytics ---
    def student_analytics(self, user):
        submissions = Submission.objects.filter(student=user)
        grades = Grade.objects.filter(submission__student=user).select_related("submission__assignment")

        valid_scores = [g.score for g in grades if g.score is not None]
        gpa = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        total_assignments = Assignment.objects.filter(course__enrollments__student=user).count()
        completed_assignments = submissions.values("assignment").distinct().count()
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments else 0

        grade_distribution = {}
        gpa_trend = []
        for g in grades:
            if g.letter:
                grade_distribution[g.letter] = grade_distribution.get(g.letter, 0) + 1
            if g.score is not None:
                gpa_trend.append({
                    "assignment": g.submission.assignment.title,
                    "score": g.score
                })

        serializer = StudentAnalyticsSerializer({
            "gpa": round(gpa, 2),
            "completion_rate": round(completion_rate, 2),
            "grades_count": grades.count(),
            "assignments_count": total_assignments,
            "grade_distribution": grade_distribution,
            "gpa_trend": gpa_trend,
        })
        return Response(serializer.data)

    # --- Instructor analytics ---
    def instructor_analytics(self, user):
        courses = Course.objects.filter(instructor=user)
        assignments = Assignment.objects.filter(course__instructor=user)
        submissions = Submission.objects.filter(assignment__course__instructor=user)
        grades = Grade.objects.filter(submission__assignment__course__instructor=user)

        course_performance = {}
        performance_trend = []
        for course in courses:
            course_grades = grades.filter(submission__assignment__course=course, score__isnull=False)
            avg_score = sum(g.score for g in course_grades) / course_grades.count() if course_grades.exists() else 0
            course_performance[str(course.title)] = round(avg_score, 2)
            performance_trend.append({
                "course": course.title,
                "average_score": round(avg_score, 2)
            })

        on_time = submissions.filter(submitted_at__lte=F("assignment__due_date")).count()
        total_submissions = submissions.count()
        timeliness_rate = (on_time / total_submissions * 100) if total_submissions else 0

        serializer = InstructorAnalyticsSerializer({
            "courses_taught": courses.count(),
            "assignments_created": assignments.count(),
            "submissions_received": submissions.count(),
            "grades_given": grades.count(),
            "course_performance": course_performance,
            "submission_timeliness_rate": round(timeliness_rate, 2),
            "performance_trend": performance_trend,
        })
        return Response(serializer.data)

    # --- Admin analytics ---
    def admin_analytics(self):
        courses = Course.objects.all()
        students = CustomUser.objects.filter(role="student")
        instructors = CustomUser.objects.filter(role="instructor")
        submissions = Submission.objects.all()
        grades = Grade.objects.all()

        valid_scores = [g.score for g in grades if g.score is not None]
        global_gpa = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        grade_distribution = {}
        for g in grades:
            if g.letter:
                grade_distribution[g.letter] = grade_distribution.get(g.letter, 0) + 1

        # ✅ Use correct related_name "enrollments"
        course_enrollment_stats = {
            course.title: course.enrollments.count()
            for course in courses
        }

        enrollment_trend = [
            {
                "course": course.title,
                "enrollment_count": course.enrollments.count()
            }
            for course in courses
        ]

        serializer = AdminAnalyticsSerializer({
            "total_courses": courses.count(),
            "total_students": students.count(),
            "total_instructors": instructors.count(),
            "total_submissions": submissions.count(),
            "total_grades": grades.count(),
            "global_gpa": round(global_gpa, 2),
            "grade_distribution": grade_distribution,
            "course_enrollment_stats": course_enrollment_stats,
            "enrollment_trend": enrollment_trend,
        })
        return Response(serializer.data)

    # --- Explicit role-based endpoints ---
    @action(detail=False, methods=["get"], url_path="student", permission_classes=[permissions.IsAuthenticated, IsStudent])
    def student(self, request):
        return self.student_analytics(request.user)

    @action(detail=False, methods=["get"], url_path="instructor", permission_classes=[permissions.IsAuthenticated, IsInstructor])
    def instructor(self, request):
        return self.instructor_analytics(request.user)

    @action(detail=False, methods=["get"], url_path="admin", permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def admin(self, request):
        return self.admin_analytics()

    @action(detail=False, methods=["get"], url_path="overview", permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def overview(self, request):
        return self.admin_analytics()

    @action(detail=True, methods=["get"], url_path="course", permission_classes=[permissions.IsAuthenticated, IsInstructor])
    def course(self, request, pk=None):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=404)

        enrollments = course.enrollments.count()  # ✅ use correct related_name
        grades = Grade.objects.filter(submission__assignment__course=course)
        valid_scores = [g.score for g in grades if g.score is not None]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        return Response({
            "course": course.title,
            "enrollments": enrollments,
            "average_score": round(avg_score, 2),
        })
