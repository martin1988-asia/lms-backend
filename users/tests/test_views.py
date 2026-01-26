from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Module
from assignments.models import Assignment, Submission


class UsersViewsTests(TestCase):
    """
    Comprehensive tests for users/views.py.
    Covers denial paths, success paths, list/retrieve, update/delete,
    perform_create logic, and registration.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="password123", role="admin", username="admin1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="password123", role="student", username="student1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="password123", role="instructor", username="instructor1"
        )
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        self.module = Module.objects.create(title="Module 1", course=self.course)
        self.assignment = Assignment.objects.create(title="Homework", course=self.course, created_by=self.instructor)
        self.submission = Submission.objects.create(student=self.student, assignment=self.assignment, content="Answer")

    # --- UserViewSet ---
    def test_user_create_denied_for_non_admin(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/users/users/", {"email": "new@example.com", "password": "password123"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/users/users/", {
            "email": "new@example.com", "password": "password123", "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_users_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_student_only_self(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_users_instructor_only_self(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_users_unauthenticated(self):
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- CourseViewSet ---
    def test_course_create_denied_for_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/users/courses/", {"title": "New Course"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_create_course_and_is_assigned(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/users/courses/", {"title": "Physics 101"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data["id"]
        course = Course.objects.get(id=course_id)
        self.assertEqual(course.instructor, self.instructor)

    def test_list_courses_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/users/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_courses_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/users/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_courses_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/users/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_courses_unauthenticated(self):
        response = self.client.get("/users/courses/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- ModuleViewSet ---
    def test_module_create_denied_for_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/users/modules/", {"title": "New Module", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_create_module(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/users/modules/", {"title": "Module 2", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_module(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/users/modules/", {"title": "Module 3", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_module_create_unauthenticated_denied(self):
        response = self.client.post("/users/modules/", {"title": "Module 4", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_module(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.delete(f"/users/modules/{self.module.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --- AssignmentViewSet ---
    def test_assignment_create_denied_for_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/users/assignments/", {"title": "New Assignment", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignment_create_denied_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/users/assignments/", {"title": "New Assignment", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_can_create_assignment_and_is_assigned(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/users/assignments/", {"title": "Lab Work", "course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment_id = response.data["id"]
        assignment = Assignment.objects.get(id=assignment_id)
        self.assertEqual(assignment.created_by, self.instructor)

    def test_list_assignments_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/users/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_assignments_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/users/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_assignments_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/users/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_assignments_unauthenticated(self):
        response = self.client.get("/users/assignments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_assignment(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.put(f"/users/assignments/{self.assignment.id}/", {
            "title": "Updated HW", "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- SubmissionViewSet ---
    def test_submission_create_denied_for_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/users/submissions/", {"assignment": self.assignment.id, "content": "Answer"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_create_denied_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/users/submissions/", {"assignment": self.assignment.id, "content": "Answer"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_create_submission_and_is_assigned(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/users/submissions/", {"assignment": self.assignment.id, "content": "My Answer"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission_id = response.data["id"]
        submission = Submission.objects.get(id=submission_id)
        self.assertEqual(submission.student, self.student)

        def test_list_submissions_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/users/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_submissions_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/users/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_submissions_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/users/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_submissions_unauthenticated(self):
        response = self.client.get("/users/submissions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_course(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.put(f"/users/courses/{self.course.id}/", {"title": "Updated Course"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_submission(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(f"/users/submissions/{self.submission.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --- Registration ---
    def test_register_user_valid(self):
        response = self.client.post("/users/register/", {
            "email": "newuser@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_invalid(self):
        response = self.client.post("/users/register/", {
            "email": "",  # invalid email
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        # Attempt to register with an email that already exists
        response = self.client.post("/users/register/", {
            "email": "student@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
