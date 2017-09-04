import json
from mock import patch
import collections
from datetime import datetime
from cStringIO import StringIO
from txwrapplog import wrapp_observer, Logger




class TestWrappObserver(object):
    @patch('txwrapplog._timestamp')
    def setup(self, timestamp_mock):
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        timestamp_mock.return_value = self.timestamp
        self.msg = 'Hello'
        self.service = "api"
        self.out = StringIO()
        self.log = Logger(observer=wrapp_observer(self.out, service=self.service))

    def _generate_output(self, level):
        res = collections.OrderedDict()
        res['level'] = level
        res['msg'] = self.msg
        res['service'] = self.service
        res['timestamp'] = self.timestamp
        res['namespace'] = 'tests'
        return '%s\n' % (json.dumps(res))

    def test_debug(self):
        self.log.debug(self.msg)
        self.assert_output(self._generate_output('debug'))

    def test_info(self):
        self.log.info(self.msg)
        self.assert_output(self._generate_output('info'))

    def test_warn(self):
        self.log.warn(self.msg)
        self.assert_output(self._generate_output('warning'))

    def test_error(self):
        self.log.error(self.msg)
        self.assert_output(self._generate_output('error'))

    def test_critical(self):
        self.log.critical(self.msg)
        self.assert_output(self._generate_output('error'))

    def test_failure(self):
        try:
            1/0
        except Exception:
            self.log.failure(self.msg)
        actual = self.get_output()
        expected_start = '{"level": "error", "msg": "%s"' % (self.msg)
        assert actual.startswith(expected_start)

    def get_output(self):
        self.out.reset()
        return self.out.read()

    def assert_output(self, expected):
        actual = self.get_output()
        assert actual == expected, repr(actual)
