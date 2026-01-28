import sys
import importlib
from django.test import SimpleTestCase
from unittest.mock import patch


class ManagePyTests(SimpleTestCase):
    def test_main_runs_successfully(self):
        manage = importlib.import_module("manage")
        with patch.object(sys, "argv", ["manage.py", "check"]):
            # Should run without raising
            manage.main()

    def test_main_importerror_branch(self):
        manage = importlib.import_module("manage")
        with patch.dict("sys.modules", {"django.core.management": None}):
            with self.assertRaises(ImportError):
                manage.main()
