from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio


class DrawDemoTestCase(TestCase):
    """Tests get_pos event"""

    def setUp(self):
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_draw_square(self):
        """Test get_pos event with unregistered manipulator"""
        self.sio.emit('register_manipulator', 2)
        self.sio.emit('bypass_calibration', 2)

        drop_depth = 10500
        drive_speed = 5000
        draw_speed = 4000

        # Home position
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [10000,
                                                                10000, 10000,
                                                                0],
                                   'speed': drive_speed}, callback=self.mock)

        # Move to 0, 0
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 10000,
                                                                0],
                                   'speed': drive_speed}, callback=self.mock)

        # Drop marker
        self.sio.emit('drive_to_depth',
                      {'manipulator_id': 2, 'depth': drop_depth,
                       'speed': draw_speed},
                      callback=self.mock)

        # 20000, 0, 10000, 12000
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [20000, 0,
                                                                10000,
                                                                drop_depth],
                                   'speed': draw_speed}, callback=self.mock)

        # 20000, 20000, 10000, 12000
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [20000, 20000,
                                                                10000,
                                                                drop_depth],
                                   'speed': draw_speed}, callback=self.mock)

        # 0, 20000, 10000, 12000
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 20000,
                                                                10000,
                                                                drop_depth],
                                   'speed': draw_speed}, callback=self.mock)

        # 0, 0, 10000, 12000
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 10000,
                                                                drop_depth],
                                   'speed': draw_speed}, callback=self.mock)

        # Raise marker
        self.sio.emit('drive_to_depth',
                      {'manipulator_id': 2, 'depth': 0, 'speed': drive_speed},
                      callback=self.mock)

        # Home position
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [10000,
                                                                10000, 10000,
                                                                0],
                                   'speed': drive_speed}, callback=self.mock)

        while self.mock.call_count != 8:
            pass

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
