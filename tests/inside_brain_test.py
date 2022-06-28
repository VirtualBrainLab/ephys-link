from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio


class InsideBrainTestCase(TestCase):
    """Tests get_pos event"""

    def setUp(self):
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_move_inside_brain(self):
        """Test goto_pos event with manipulator inside the brain"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('bypass_calibration', 1)
        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': (0, 0, 0, 0),
                                   'speed': 4000}, callback=self.mock)
        self.wait_for_callback()

        self.sio.emit('inside_brain', {'manipulator_id': 1, 'inside': True},
                      callback=self.mock)
        self.wait_for_callback()

        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': (10000, 10000,
                                                                10000, 50),
                                   'speed': 4000}, callback=self.mock)
        self.wait_for_callback()

        self.sio.emit('get_pos', 1, callback=self.mock)
        args = self.mock.call_args.args

        self.sio.emit('inside_brain', {'manipulator_id': 1, 'inside': False},
                      callback=self.mock)
        self.wait_for_callback()
        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': (10000, 10000,
                                                                10000, 10000),
                                   'speed': 4000}, callback=self.mock)
        self.wait_for_callback()

        self.assertLess(abs(args[1][0]), 1)
        self.assertLess(abs(args[1][1]), 1)
        self.assertLess(abs(args[1][2]), 1)

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
