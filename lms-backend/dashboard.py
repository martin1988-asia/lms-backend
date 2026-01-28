from admin_tools.dashboard import modules, Dashboard
from django.contrib.auth import get_user_model
from courses.models import Course
from assignments.models import Submission
from grades.models import Grade

User = get_user_model()

class CustomIndexDashboard(Dashboard):
    """
    Custom dashboard for the admin index page.
    """

    def init_with_context(self, context):
        # ✅ Quick links
        self.children.append(modules.LinkList(
            title='Quick Links',
            layout='inline',
            children=[
                ('Return to site', '/'),
                ('Manage Users', '/admin/accounts/customuser/'),
                ('Manage Courses', '/admin/courses/course/'),
                ('Manage Assignments', '/admin/assignments/assignment/'),
            ]
        ))

        # ✅ Stats section
        self.children.append(modules.Group(
            title="System Stats",
            children=[
                modules.LinkList(
                    title="Overview",
                    children=[
                        (f"Total Users: {User.objects.count()}", '/admin/accounts/customuser/'),
                        (f"Total Courses: {Course.objects.count()}", '/admin/courses/course/'),
                        (f"Total Submissions: {Submission.objects.count()}", '/admin/assignments/submission/'),
                        (f"Total Grades: {Grade.objects.count()}", '/admin/grades/grade/'),
                    ]
                ),
            ]
        ))

        # ✅ Recent actions
        self.children.append(modules.RecentActions(
            title='Recent Actions',
            limit=10
        ))
