from unittest import TestCase
from unittest.mock import Mock

# noinspection PyPackageRequirements
import socketio


class GetManipulatorsTestCase(TestCase):
    """Tests get_pos event"""

    def setUp(self):
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect("http://localhost:8080")

    def test_get_manipulators(self):
        """Test get_pos event with unregistered manipulator"""
        self.sio.emit("get_manipulators", callback=self.mock)
        self.wait_for_callback()

        self.assertEqual(self.mock.call_args.args[0]["error"], "")

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
