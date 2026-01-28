import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
django.setup()

from courses.models import Course
from assignments.models import Assignment
from grades.models import Grade

# Clear existing data (optional)
Course.objects.all().delete()
Assignment.objects.all().delete()
Grade.objects.all().delete()

# Create sample courses
math = Course.objects.create(title="Mathematics 101", description="Introductory algebra and geometry")
history = Course.objects.create(title="History 201", description="World history overview")
cs = Course.objects.create(title="Computer Science 301", description="Python programming basics")

# Create multiple assignments per course
math_hw1 = Assignment.objects.create(course=math, title="Algebra Homework", description="Solve equations")
math_hw2 = Assignment.objects.create(course=math, title="Geometry Quiz", description="Shapes and angles")

history_hw1 = Assignment.objects.create(course=history, title="Essay on WWII", description="Write 1000 words")
history_hw2 = Assignment.objects.create(course=history, title="Cold War Presentation", description="Prepare slides")

cs_hw1 = Assignment.objects.create(course=cs, title="Python Project", description="Build a calculator")
cs_hw2 = Assignment.objects.create(course=cs, title="Data Structures Homework", description="Implement linked list")

# Create multiple grades per assignment
Grade.objects.create(assignment=math_hw1, score=85, feedback="Good work, but check Q3")
Grade.objects.create(assignment=math_hw1, score=90, feedback="Excellent improvement")

Grade.objects.create(assignment=math_hw2, score=70, feedback="Needs more practice on angles")
Grade.objects.create(assignment=math_hw2, score=88, feedback="Solid understanding of geometry")

Grade.objects.create(assignment=history_hw1, score=92, feedback="Excellent analysis")
Grade.objects.create(assignment=history_hw1, score=76, feedback="Decent effort, but missing citations")

Grade.objects.create(assignment=history_hw2, score=80, feedback="Presentation was clear")
Grade.objects.create(assignment=history_hw2, score=95, feedback="Outstanding slides and delivery")

Grade.objects.create(assignment=cs_hw1, score=78, feedback="Functional, but needs better error handling")
Grade.objects.create(assignment=cs_hw1, score=89, feedback="Well structured code")

Grade.objects.create(assignment=cs_hw2, score=84, feedback="Correct implementation")
Grade.objects.create(assignment=cs_hw2, score=91, feedback="Efficient and clean solution")

print("✅ Seed data inserted successfully with multiple assignments and grades!")
