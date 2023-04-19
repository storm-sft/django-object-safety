import sys
from unittest import TestSuite

from boot_django import boot_django

# from django.db.models import loading

boot_django()

default_labels = ["safety", ]


def get_suite(test_labels=None):
    from django.test.runner import DiscoverRunner

    if test_labels is None:
        test_labels = default_labels

    runner = DiscoverRunner(verbosity=1)
    failures = runner.run_tests(test_labels)

    if failures:
        sys.exit(failures)

    return TestSuite()


if __name__ == "__main__":
    labels = default_labels
    if len(sys.argv[1:]) > 0:
        labels = sys.argv[1:]
    get_suite(labels)
