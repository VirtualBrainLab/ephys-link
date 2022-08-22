from unittest import TestCase
from unittest.mock import Mock

# noinspection PyPackageRequirements
import socketio

from ephys_link.common import PositionalOutputData


# noinspection DuplicatedCode
class MoveTest(TestCase):
    """Tests movement event"""

    DRIVE_SPEED = 8000

    def setUp(self) -> None:
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect("http://localhost:8080")

    def test_move_no_asserts(self):
        """Test movement without asserts"""
        self.sio.emit("register_manipulator", 1)
        self.sio.emit("register_manipulator", 2)
        self.sio.emit("bypass_calibration", 1)
        self.sio.emit("bypass_calibration", 2)
        self.sio.emit(
            "set_can_write", {"manipulator_id": 1, "can_write": True, "hours": 1}
        )
        self.sio.emit(
            "set_can_write", {"manipulator_id": 2, "can_write": True, "hours": 1}
        )

        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 1, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )
        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 2, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )

        self.sio.emit(
            "goto_pos",
            {
                "manipulator_id": 1,
                "pos": [10000, 10000, 10000, 10000],
                "speed": self.DRIVE_SPEED,
            },
            callback=self.mock,
        )
        self.sio.emit(
            "goto_pos",
            {
                "manipulator_id": 2,
                "pos": [10000, 10000, 10000, 10000],
                "speed": self.DRIVE_SPEED,
            },
            callback=self.mock,
        )

        while self.mock.call_count != 4:
            pass

    def test_move_with_asserts(self):
        """Test movement with asserts"""
        self.sio.emit("register_manipulator", 1)
        self.sio.emit("register_manipulator", 2)
        self.sio.emit("bypass_calibration", 1)
        self.sio.emit("bypass_calibration", 2)
        self.sio.emit(
            "set_can_write", {"manipulator_id": 1, "can_write": True, "hours": 1}
        )
        self.sio.emit(
            "set_can_write", {"manipulator_id": 2, "can_write": True, "hours": 1}
        )

        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 1, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )
        self.wait_for_callback()
        args = self.mock.call_args.args[0]
        self.assertEqual(args["error"], "")
        self.assertEqual(len(args["position"]), 4)

        self.sio.emit(
            "goto_pos",
            {
                "manipulator_id": 1,
                "pos": [10000, 10000, 10000, 10000],
                "speed": self.DRIVE_SPEED,
            },
            callback=self.mock,
        )
        self.wait_for_callback()

    def test_move_unregistered(self):
        """Test movement with unregistered manipulator"""
        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 1, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )
        self.wait_for_callback()
        self.mock.assert_called_with(
            PositionalOutputData([], "Manipulator not registered")
        )

    def test_move_no_write(self):
        """Test movement with no write"""
        self.sio.emit("register_manipulator", 1)
        self.sio.emit("bypass_calibration", 1)
        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 1, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )
        self.wait_for_callback()
        self.mock.assert_called_with(
            PositionalOutputData([], "Cannot write to manipulator")
        )

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
