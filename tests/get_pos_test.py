from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio


class GetPosTestCase(TestCase):
    """Tests get_pos event"""

    def setUp(self):
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_get_pos_unregistered(self):
        """Test get_pos event with unregistered manipulator"""
        self.sio.emit('get_pos', 1, callback=self.mock)
        self.sio.emit('bypass_calibration', 1)
        self.wait_for_callback()

        self.mock.assert_called_with(1, [], 'Manipulator not registered')

    def test_get_pos_registered(self):
        """Test get_pos event with registered manipulator"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('bypass_calibration', 1)
        self.sio.emit('get_pos', 1, callback=self.mock)
        self.wait_for_callback()

        args = self.mock.call_args.args
        self.assertEqual(args[0], 1)
        self.assertEqual(len(args[1]), 4)
        self.assertEqual(args[2], '')

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
