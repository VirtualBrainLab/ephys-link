from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio


class MoveTest(TestCase):
    """Tests movement event"""

    def setUp(self) -> None:
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_move_no_asserts(self):
        """Test movement without asserts"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('register_manipulator', 2)

        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                                   'speed': 2000},
                      callback=self.mock)
        self.sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 0, 0],
                                   'speed': 2000},
                      callback=self.mock)

        self.sio.emit('goto_pos',
                      {'manipulator_id': 1,
                       'pos': [10000, 10000, 10000, 10000],
                       'speed': 2000}, callback=self.mock)
        self.sio.emit('goto_pos',
                      {'manipulator_id': 2,
                       'pos': [10000, 10000, 10000, 10000],
                       'speed': 2000}, callback=self.mock)

        while self.mock.call_count != 4:
            pass

    def test_move_with_asserts(self):
        """Test movement with asserts"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('register_manipulator', 2)

        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                                   'speed': 2000},
                      callback=self.mock)
        self.wait_for_callback()
        args = self.mock.call_args.args
        self.assertEqual(args[0], 1)
        self.assertEqual(len(args[1]), 4)
        self.assertEqual(args[2], '')

        self.sio.emit('goto_pos', {'manipulator_id': 1,
                                   'pos': [10000, 10000, 10000, 10000],
                                   'speed': 2000}, callback=self.mock)
        while self.mock.call_count != 2:
            pass

    def test_move_unregistered(self):
        """Test movement with unregistered manipulator"""
        self.sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                                   'speed': 2000},
                      callback=self.mock)
        self.wait_for_callback()
        self.mock.assert_called_with(1, [], 'Manipulator not registered')

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
