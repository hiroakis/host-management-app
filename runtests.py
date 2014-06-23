from unittest import (
    TestLoader, TestSuite, TextTestRunner
)

from srvadm.tests.test_validator import TestValidator
from srvadm.tests.test_models import (
    TestRole, TestIP, TestReloIP, TestHost,
    TestRoleMap, TestReloIPMap
)
from srvadm.tests.test_api import TestApi
from srvadm.tests.test_api_hosts_output import TestHostsOutput

def test_all():
    loader = TestLoader()
    suites = [\
        loader.loadTestsFromTestCase(TestRole), \
        loader.loadTestsFromTestCase(TestIP), \
        loader.loadTestsFromTestCase(TestReloIP), \
        loader.loadTestsFromTestCase(TestHost), \
        loader.loadTestsFromTestCase(TestRoleMap), \
        loader.loadTestsFromTestCase(TestReloIPMap), \
        loader.loadTestsFromTestCase(TestApi), \
        loader.loadTestsFromTestCase(TestHostsOutput), \
        loader.loadTestsFromTestCase(TestValidator), \
    ]

    testsuites = TestSuite(suites)
    runner = TextTestRunner()
    runner.run(testsuites)

if __name__ == '__main__':
    test_all()
