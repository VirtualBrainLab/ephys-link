from vbl_aquarium.models.unity import Vector3, Vector4

# Dummy values for testing.
DUMMY_STRING = "Dummy String"
DUMMY_SMALL_STRING = "dummy"
DUMMY_INT = 3
DUMMY_STRING_LIST: list[str] = [DUMMY_STRING, DUMMY_SMALL_STRING]
DUMMY_VECTOR3 = Vector3(x=1.0, y=2.0, z=3.0)
DUMMY_VECTOR4 = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)
DUMMY_EXCEPTION = RuntimeError("Test runtime error")
