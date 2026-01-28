from django.test import TestCase
from analytics.models import AnalyticsLog

class AnalyticsLogModelTests(TestCase):
    def test_str_method(self):
        log = AnalyticsLog.objects.create(message="Test entry")
        self.assertEqual(str(log), "Log: Test entry")

    def test_meta_verbose_names(self):
        self.assertEqual(str(AnalyticsLog._meta.verbose_name), "Analytics Log")
        self.assertEqual(str(AnalyticsLog._meta.verbose_name_plural), "Analytics Logs")

    def test_meta_ordering(self):
        log1 = AnalyticsLog.objects.create(message="First")
        log2 = AnalyticsLog.objects.create(message="Second")
        logs = AnalyticsLog.objects.all()
        # ordering is by -created_at, so latest log2 comes first
        self.assertEqual(logs[0], log2)
