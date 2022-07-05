from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio


class CalibrationTestCase(TestCase):
    """Tests calibration event"""

    def setUp(self):
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_calibrate_unregistered(self):
        """Test calibrate event with unregistered manipulator"""
        self.sio.emit('calibrate', 1, callback=self.mock)
        self.wait_for_callback()

        self.mock.assert_called_with(1, 'Manipulator not registered')

    def test_get_pos_uncalibrated(self):
        """Test get_pos event with uncalibrated manipulator"""
        self.sio.emit('register_manipulator', 1, callback=self.mock)
        self.wait_for_callback()
        self.sio.emit('get_pos', 1, callback=self.mock)
        self.wait_for_callback()
        self.mock.assert_called_with(1, [], 'Manipulator not calibrated')

    def test_move_uncalibrated(self):
        """Test move event with uncalibrated manipulator"""
        self.sio.emit('register_manipulator', 1, callback=self.mock)
        self.wait_for_callback()
        self.sio.emit('set_can_write',
                      {'manipulator_id': 1, 'can_write': True, 'hours': 1})
        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                                   'speed': 2000},
                      callback=self.mock)
        self.wait_for_callback()
        self.mock.assert_called_with(1, [], 'Manipulator not calibrated')

    def test_calibrate_registered(self):
        """Test calibrate event with registered manipulator"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('register_manipulator', 2)
        self.sio.emit('set_can_write',
                      {'manipulator_id': 1, 'can_write': True, 'hours': 1})
        self.sio.emit('set_can_write',
                      {'manipulator_id': 2, 'can_write': True, 'hours': 1})
        self.sio.emit('calibrate', 1, callback=self.mock)
        self.sio.emit('calibrate', 2, callback=self.mock)

        while self.mock.call_count != 2:
            pass

        args = self.mock.call_args.args
        self.assertEqual(args[1], '')

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
