
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    test_case = f".{sys.argv[1]}" if len(sys.argv) >= 2 else ''
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)
    failures = test_runner.run_tests(["geospaas_rest_api.tests" + test_case])
    sys.exit(bool(failures))
