from unittest import TestCase
from unittest.mock import Mock
# noinspection PyPackageRequirements
import socketio
from nptraj_sensapex_link.common import IdOutputData


class RegisterManipulatorTestCase(TestCase):
    """Tests manipulator registration"""

    def setUp(self) -> None:
        """Setup test case"""
        self.sio = socketio.Client()
        self.mock = Mock()

        self.sio.connect('http://localhost:8080')

    def test_register_manipulator(self):
        """Tests registering a manipulator"""
        self.sio.emit('register_manipulator', 1, callback=self.mock)
        self.wait_for_callback()

        self.mock.assert_called_with(IdOutputData(1, ''))

    def test_re_register_manipulator(self):
        """Test re-registering a manipulator"""
        self.sio.emit('register_manipulator', 1)
        self.sio.emit('register_manipulator', 1, callback=self.mock)
        self.wait_for_callback()

        self.mock.assert_called_with(
            IdOutputData(1, 'Manipulator already registered'))

    def test_register_unknown_manipulator(self):
        """Test registering an unknown manipulator"""
        self.sio.emit('register_manipulator', 3, callback=self.mock)
        self.wait_for_callback()

        self.mock.assert_called_with(IdOutputData(3, 'Manipulator not found'))

    def tearDown(self) -> None:
        """Cleanup test case"""
        self.sio.disconnect()

    def wait_for_callback(self):
        """Wait for callback to be called"""
        while not self.mock.called:
            pass
