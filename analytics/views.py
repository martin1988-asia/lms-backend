from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import CustomUser
from courses.models import Course
from enrollments.models import Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Robust analytics ViewSet:
    - Students: GPA, completion rate, grades count, assignments count
    - Instructors: teaching stats, submissions, grades, per-course breakdown
    - Admins: global stats, grade distribution, course enrollment, overview, per-course analytics
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Auto-detect role and return appropriate analytics.
        """
        user = request.user
        role = getattr(user, "role", None)

        if role == "student":
            return self.student_analytics(user)
        elif role == "instructor":
            return self.instructor_analytics(user)
        elif role == "admin":
            return self.admin_analytics()

        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # --- Student analytics ---
    def student_analytics(self, user):
        submissions = Submission.objects.filter(student=user).select_related("assignment")
        grades = Grade.objects.filter(submission__student=user)

        gpa = grades.aggregate(avg=Avg("score"))["avg"] or 0.0
        total_assignments = Assignment.objects.filter(course__enrollments__student=user).count()
        completed_assignments = submissions.values("assignment").distinct().count()
        completion_rate = (completed_assignments / total_assignments * 100.0) if total_assignments else 0.0

        return Response({
            "gpa": round(gpa, 2),
            "completion_rate": round(completion_rate, 2),
            "grades_count": grades.count(),
            "assignments_count": total_assignments,
        })

    # --- Instructor analytics ---
    def instructor_analytics(self, user):
        courses = Course.objects.filter(instructor=user)
        assignments = Assignment.objects.filter(course__instructor=user)
        submissions = Submission.objects.filter(assignment__course__instructor=user)
        grades = Grade.objects.filter(submission__assignment__course__instructor=user)

        # Per-course breakdown
        course_performance = []
        for course in courses:
            course_assignments = Assignment.objects.filter(course=course)
            course_submissions = Submission.objects.filter(assignment__course=course)
            course_grades = Grade.objects.filter(submission__assignment__course=course)
            avg_score = course_grades.aggregate(avg=Avg("score"))["avg"] or 0.0

            course_performance.append({
                "course": course.title,
                "assignments_count": course_assignments.count(),
                "submissions_count": course_submissions.count(),
                "grades_count": course_grades.count(),
                "average_score": round(avg_score, 2),
            })

        return Response({
            "courses_taught": courses.count(),
            "assignments_created": assignments.count(),
            "submissions_received": submissions.count(),
            "grades_given": grades.count(),
            "course_performance": course_performance,
        })

    # --- Admin analytics ---
    def admin_analytics(self):
        courses = Course.objects.all()
        students = CustomUser.objects.filter(role="student")
        instructors = CustomUser.objects.filter(role="instructor")
        submissions = Submission.objects.all()
        grades = Grade.objects.all()

        global_gpa = grades.aggregate(avg=Avg("score"))["avg"] or 0.0

        grade_distribution = {
            g["letter"]: g["count"] for g in grades.values("letter").annotate(count=Count("id"))
            if g["letter"]
        }

        course_enrollment_stats = {
            course.title: Enrollment.objects.filter(course=course).values("student").distinct().count()
            for course in courses
        }

        return Response({
            "total_courses": courses.count(),
            "total_students": students.count(),
            "total_instructors": instructors.count(),
            "total_submissions": submissions.count(),
            "total_grades": grades.count(),
            "global_gpa": round(global_gpa, 2),
            "grade_distribution": grade_distribution,
            "course_enrollment_stats": course_enrollment_stats,
        })

    # --- Explicit role-based endpoints ---
    @action(detail=False, methods=["get"], url_path="student")
    def student(self, request):
        if getattr(request.user, "role", None) != "student":
            return Response(
                {"detail": "You do not have permission to access student analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.student_analytics(request.user)

    @action(detail=False, methods=["get"], url_path="instructor")
    def instructor(self, request):
        if getattr(request.user, "role", None) != "instructor":
            return Response(
                {"detail": "You do not have permission to access instructor analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.instructor_analytics(request.user)

    @action(detail=False, methods=["get"], url_path="admin")
    def admin(self, request):
        if getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "You do not have permission to access admin analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.admin_analytics()

    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        if getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "You do not have permission to access overview analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        courses = Course.objects.all()
        grades = Grade.objects.all()
        global_gpa = grades.aggregate(avg=Avg("score"))["avg"] or 0.0

        return Response({
            "courses": courses.count(),
            "grades": grades.count(),
            "global_gpa": round(global_gpa, 2),
        })

    @action(detail=True, methods=["get"], url_path="course")
    def course(self, request, pk=None):
        if getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "You do not have permission to access course analytics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignments = Assignment.objects.filter(course=course)
        submissions = Submission.objects.filter(assignment__course=course)
        grades = Grade.objects.filter(submission__assignment__course=course)
        avg_score = grades.aggregate(avg=Avg("score"))["avg"] or 0.0

        return Response({
            "course": course.title,
            "assignments_count": assignments.count(),
            "submissions_count": submissions.count(),
            "grades_count": grades.count(),
            "average_score": round(avg_score, 2),
        })
