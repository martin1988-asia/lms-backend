from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Enrollment


class CourseEnrollmentViewsTests(TestCase):
    """
    Comprehensive tests for courses/views.py.
    Covers get_queryset for each role, create success/denial,
    and perform_create logic for both CourseViewSet and EnrollmentViewSet.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="password123",
            role="admin",
            username="admin1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="password123",
            role="student",
            username="student1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="password123",
            role="instructor",
            username="instructor1"
        )
        self.course = Course.objects.create(
            title="Math 101",
            instructor=self.instructor
        )

    # --- CourseViewSet ---
    def test_course_queryset_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_queryset_student(self):
        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_queryset_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_queryset_no_role(self):
        user = CustomUser.objects.create_user(
            email="norole@example.com",
            password="password123",
            username="norole1"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_course_queryset_unauthenticated(self):
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_create_instructor_success_and_auto_assign(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/api/courses/", {"title": "Physics 101"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data["id"]
        course = Course.objects.get(id=course_id)
        self.assertEqual(course.instructor, self.instructor)

    def test_course_create_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/courses/", {"title": "Chemistry 101"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_create_student_denied(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/api/courses/", {"title": "Biology 101"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_create_no_role_denied(self):
        user = CustomUser.objects.create_user(
            email="norole2@example.com",
            password="password123",
            username="norole2"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post("/api/courses/", {"title": "History 101"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- EnrollmentViewSet ---
    def test_enrollment_queryset_student(self):
        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_queryset_instructor(self):
        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_queryset_admin(self):
        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_queryset_no_role(self):
        user = CustomUser.objects.create_user(
            email="norole3@example.com",
            password="password123",
            username="norole3"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_enrollment_queryset_unauthenticated(self):
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enrollment_create_student_success_and_auto_assign(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/api/enrollments/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        enrollment_id = response.data["id"]
        enrollment = Enrollment.objects.get(id=enrollment_id)
        self.assertEqual(enrollment.student, self.student)

    def test_enrollment_create_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/enrollments/", {
            "course": self.course.id,
            "student": self.student.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enrollment_create_admin_missing_student_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/enrollments/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_create_admin_invalid_student_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/enrollments/", {
            "course": self.course.id,
            "student": 999
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_create_instructor_denied(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/api/enrollments/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enrollment_create_no_role_denied(self):
        user = CustomUser.objects.create_user(
            email="norole4@example.com",
            password="password123",
            username="norole4"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post("/api/enrollments/", {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
