from unittest import TestCase
from unittest.mock import Mock

# noinspection PyPackageRequirements
import socketio


# noinspection DuplicatedCode
class StopTest(TestCase):
    """Tests stop event"""

    DRIVE_SPEED = 8000

    def setUp(self) -> None:
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect("http://localhost:8080")

    def test_stop_event(self):
        """Test stopping movement with event"""
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
        )
        self.sio.emit(
            "goto_pos",
            {
                "manipulator_id": 2,
                "pos": [10000, 10000, 10000, 10000],
                "speed": self.DRIVE_SPEED,
            },
        )

        while self.mock.call_count != 2:
            pass

        self.sio.sleep(1)

        # Test stop
        self.mock.called = False
        self.sio.emit("stop", callback=self.mock)
        self.wait_for_callback()
        stop_arg = self.mock.call_args.args[0]

        # Test no calibration
        self.sio.emit(
            "goto_pos",
            {"manipulator_id": 1, "pos": [0, 0, 0, 0], "speed": self.DRIVE_SPEED},
            callback=self.mock,
        )
        self.wait_for_callback()
        args = self.mock.call_args.args[0]

        # Bring back to home
        self.mock.call_count = 0
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

        while self.mock.call_count != 2:
            pass

        # Asserts
        self.assertTrue(stop_arg)
        self.assertEqual(len(args), 2)
        self.assertEqual(args["error"], "Cannot write to manipulator")

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
        self.mock.called = False
