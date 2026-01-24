from django.conf import settings
from django.db import models
from courses.models import Course


class Enrollment(models.Model):
    """
    Enrollment model links a student to a course.
    - Students enroll in courses.
    - Instructors and admins can view/manage enrollments.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
        help_text="Student enrolled in the course"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
        help_text="Course the student is enrolled in"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")
        ]
        ordering = ["-enrolled_at"]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        student_name = getattr(self.student, "username", "Unknown Student")
        course_title = getattr(self.course, "title", "Unknown Course")
        return f"{student_name} enrolled in {course_title}"
