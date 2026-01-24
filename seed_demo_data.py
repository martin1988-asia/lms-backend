import random
import datetime
from django.utils import timezone

from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


def create_user(username, email, password, role):
    """
    Helper function to create or update a user with proper password hashing.
    """
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={"email": email, "role": role}
    )
    # Always reset password to ensure it's hashed correctly
    user.set_password(password)
    user.role = role
    user.save()
    return user


def run():
    # --- Create demo instructor ---
    instructor = create_user(
        "instructor_demo",
        "instructor_demo@example.com",
        "testpass123",
        "instructor"
    )

    # --- Create demo courses ---
    math, _ = Course.objects.update_or_create(
        title="Math 101",
        defaults={"description": "Introductory Algebra", "instructor": instructor}
    )
    physics, _ = Course.objects.update_or_create(
        title="Physics 101",
        defaults={"description": "Mechanics and Motion", "instructor": instructor}
    )

    # --- Create assignments ---
    hw1, _ = Assignment.objects.update_or_create(
        course=math,
        title="Homework 1",
        defaults={
            "description": "Algebra problems",
            "due_date": timezone.now() + datetime.timedelta(days=7)
        }
    )
    hw2, _ = Assignment.objects.update_or_create(
        course=math,
        title="Homework 2",
        defaults={
            "description": "Geometry problems",
            "due_date": timezone.now() + datetime.timedelta(days=14)
        }
    )
    lab1, _ = Assignment.objects.update_or_create(
        course=physics,
        title="Lab Report 1",
        defaults={
            "description": "Motion experiments",
            "due_date": timezone.now() + datetime.timedelta(days=10)
        }
    )

    # --- Generate 10 random students ---
    for i in range(1, 11):
        student = create_user(
            f"student_demo{i}",
            f"student_demo{i}@example.com",
            "testpass123",
            "student"
        )

        # Enroll each student in both courses
        Enrollment.objects.get_or_create(course=math, student=student)
        Enrollment.objects.get_or_create(course=physics, student=student)

        # Create submissions for each assignment
        for assignment in [hw1, hw2, lab1]:
            submission, _ = Submission.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={"content": f"Submission by {student.username}"}
            )

            # Assign a random grade between 60 and 100
            Grade.objects.update_or_create(
                submission=submission,
                instructor=instructor,
                defaults={
                    "score": random.randint(60, 100),
                    "feedback": "Auto-generated grade"
                }
            )

    print("✅ Demo data with 10 random students seeded successfully!")
