from cStringIO import StringIO
from txwrapplog import wrapp_observer, Logger




class TestWrappObserver(object):
    def setup(self):
        self.out = StringIO()
        self.log = Logger(observer=wrapp_observer(self.out))

    def test_debug(self):
        self.log.debug('Hello!')
        self.assert_output('DEBUG {"level": "debug", "msg": "Hello!", "namespace": "tests"}\n')

    def test_info(self):
        self.log.info('Hello!')
        self.assert_output('INFO {"level": "info", "msg": "Hello!", "namespace": "tests"}\n')

    def test_warn(self):
        self.log.warn('Hello!')
        self.assert_output('WARNING {"level": "warning", "msg": "Hello!", "namespace": "tests"}\n')

    def test_error(self):
        self.log.error('Hello!')
        self.assert_output('ERROR {"level": "error", "msg": "Hello!", "namespace": "tests"}\n')

    def test_critical(self):
        self.log.critical('Hello!')
        self.assert_output('ERROR {"level": "error", "msg": "Hello!", "namespace": "tests"}\n')

    def test_failure(self):
        try:
            1/0
        except Exception:
            self.log.failure('Hello!')
        actual = self.get_output()
        assert actual.startswith('ERROR {"level": "error", "msg": "Hello!", "namespace": "tests"')

    def get_output(self):
        self.out.reset()
        return self.out.read()

    def assert_output(self, expected):
        actual = self.get_output()
        assert actual == expected, repr(actual)
