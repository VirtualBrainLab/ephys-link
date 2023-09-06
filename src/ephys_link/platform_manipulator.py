"""Defines what the properties and required functionality of a manipulator are.

Most functionality will be implemented on the platform handler side. This is mostly
for enforcing implementation of the stop method and hold common properties.
"""
from abc import ABC, abstractmethod


class PlatformManipulator(ABC):
    """An abstract class that defines the interface for a manipulator."""

    def __init__(self):
        """Initialize manipulator."""

        self._id = None
        self._calibrated = False
        self._inside_brain = False
        self._can_write = False
        self._reset_timer = None
        self._is_moving = False

    @abstractmethod
    def stop(self) -> None:
        """Stop all axes on manipulator

        :returns None
        """
        raise NotImplementedError
