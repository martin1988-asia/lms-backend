from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade
from assignments.serializers import AssignmentSerializer, SubmissionSerializer
from grades.serializers import GradeSerializer
from courses.serializers import CourseSerializer


class StudentDashboardView(APIView):
    """
    Dashboard view for students.
    Shows GPA, assignments count, grades count, completion rate, plus arrays of assignments, submissions, grades.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) != "student":
            return Response({"detail": "Access denied. Only students can view this dashboard."}, status=403)

        assignments = Assignment.objects.filter(course__enrollments__student=user).select_related("course")
        submissions = Submission.objects.filter(student=user).select_related("assignment")
        grades = Grade.objects.filter(submission__student=user)

        grades_count = grades.count()
        assignments_count = assignments.count()
        gpa = grades.aggregate(avg=Avg("grade"))["avg"] or 0.0
        completion_rate = (submissions.count() / assignments_count * 100.0) if assignments_count > 0 else 0.0

        return Response({
            "grades_count": grades_count,
            "assignments_count": assignments_count,
            "gpa": round(float(gpa), 2),
            "completion_rate": round(completion_rate, 2),
            "assignments": AssignmentSerializer(assignments, many=True).data,
            "submissions": SubmissionSerializer(submissions, many=True).data,
            "grades": GradeSerializer(grades, many=True).data,
        })


class InstructorDashboardView(APIView):
    """
    Dashboard view for instructors.
    Shows courses taught, assignments created, submissions received, grades given, course performance, plus arrays.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) != "instructor":
            return Response({"detail": "Access denied. Only instructors can view this dashboard."}, status=403)

        courses = Course.objects.filter(instructor=user)
        assignments = Assignment.objects.filter(course__instructor=user).select_related("course")
        submissions = Submission.objects.filter(assignment__course__instructor=user).select_related("assignment", "student")
        grades = Grade.objects.filter(submission__assignment__course__instructor=user)

        courses_taught = courses.count()
        assignments_created = assignments.count()
        submissions_received = submissions.count()
        grades_given = grades.count()

        course_performance = {
            course.title: round(
                grades.filter(submission__assignment__course=course).aggregate(avg=Avg("grade"))["avg"] or 0.0, 2
            )
            for course in courses
        }

        return Response({
            "courses_taught": courses_taught,
            "assignments_created": assignments_created,
            "submissions_received": submissions_received,
            "grades_given": grades_given,
            "course_performance": course_performance,
            "courses": CourseSerializer(courses, many=True).data,
            "assignments": AssignmentSerializer(assignments, many=True).data,
            "submissions": SubmissionSerializer(submissions, many=True).data,
            "grades": GradeSerializer(grades, many=True).data,
        })


class AdminDashboardView(APIView):
    """
    Dashboard view for admins.
    Shows global stats plus arrays of courses, assignments, submissions, grades.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) != "admin":
            return Response({"detail": "Access denied. Only admins can view this dashboard."}, status=403)

        courses = Course.objects.all()
        students = CustomUser.objects.filter(role="student")
        instructors = CustomUser.objects.filter(role="instructor")
        submissions = Submission.objects.all()
        grades = Grade.objects.all()

        total_courses = courses.count()
        total_students = students.count()
        total_instructors = instructors.count()
        total_submissions = submissions.count()
        total_grades = grades.count()
        global_gpa = grades.aggregate(avg=Avg("grade"))["avg"] or 0.0

        grade_distribution = {
            g["letter"]: g["count"] for g in grades.values("letter").annotate(count=Count("id"))
        }

        course_enrollment_stats = {
            course.title: Enrollment.objects.filter(course=course).values("student").distinct().count()
            for course in courses
        }

        return Response({
            "total_courses": total_courses,
            "total_students": total_students,
            "total_instructors": total_instructors,
            "total_submissions": total_submissions,
            "total_grades": total_grades,
            "global_gpa": round(float(global_gpa), 2),
            "grade_distribution": grade_distribution,
            "course_enrollment_stats": course_enrollment_stats,
            "courses": CourseSerializer(courses, many=True).data,
            "assignments": AssignmentSerializer(Assignment.objects.all(), many=True).data,
            "submissions": SubmissionSerializer(submissions, many=True).data,
            "grades": GradeSerializer(grades, many=True).data,
        })
