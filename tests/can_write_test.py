from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio

sio = socketio.Client()
sio.connect('http://localhost:8080')


@sio.event
def write_disabled(data):
    print(f'[EVENT]\t\t Write disabled for manipulator {data}')


# noinspection DuplicatedCode
class CanWriteTest(TestCase):
    """Tests can_write event"""
    DRIVE_SPEED = 10000

    def setUp(self) -> None:
        """Setup test case"""
        self.mock = Mock()

    def test_can_write_timer(self):
        """Test movement without asserts"""
        sio.emit('register_manipulator', 1)
        sio.emit('register_manipulator', 2)
        sio.emit('bypass_calibration', 1)
        sio.emit('bypass_calibration', 2)
        sio.emit('set_can_write',
                 {'manipulator_id': 1, 'can_write': True,
                  'hours': 0.00027777777})
        sio.emit('set_can_write',
                 {'manipulator_id': 2, 'can_write': True,
                  'hours': 0.00027777777})

        sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                              'speed': self.DRIVE_SPEED},
                 callback=self.mock)
        sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 0, 0],
                              'speed': self.DRIVE_SPEED},
                 callback=self.mock)

        sio.emit('goto_pos',
                 {'manipulator_id': 1,
                  'pos': [10000, 10000, 10000, 10000],
                  'speed': self.DRIVE_SPEED}, callback=self.mock)
        sio.emit('goto_pos',
                 {'manipulator_id': 2,
                  'pos': [10000, 10000, 10000, 10000],
                  'speed': self.DRIVE_SPEED}, callback=self.mock)

        while self.mock.call_count != 4:
            pass
        self.assertEqual(self.mock.call_args.args[2], 'Manipulator movement '
                                                      'canceled')

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
