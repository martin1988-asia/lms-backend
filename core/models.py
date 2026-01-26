#from django.db import models
#from django.conf import settings
#from courses.models import Course

#User = settings.AUTH_USER_MODEL


#class Enrollment(models.Model):
 #   """
  #  Enrollment model linking a student to a course.
   # Ensures that a student cannot be enrolled in the same course more than once.
    #"""
    #student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    #course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    #created_at = models.DateTimeField(auto_now_add=True)

    #class Meta:
     #   unique_together = ("student", "course")  # ✅ prevent duplicate enrollments
      #  ordering = ["-created_at"]               # ✅ newest enrollments first
#
 #   def __str__(self):
  #      return f"{self.student} enrolled in {self.course}"
