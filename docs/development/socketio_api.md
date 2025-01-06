# Socket.IO API

This section documents the Socket.IO API. The document is intended for developers building client applications that
communicate with the server. If you are looking for information on how to set up and run the server, see the
[installation guide](../home/installation.md)!

## Data Types

All messages on Socket.IO are passed as strings. Complex data structures are JSON encoded, converted to strings, then
sent. These structures have their JSON schema's documented
on [VBL Aquarium](https://github.com/VirtualBrainLab/vbl-aquarium/tree/main/models/schemas/ephys_link).

This documentation will reference the Pydantic versions of these models as they are extensively documented. For most
functions, their functions and responses are documented by these models. Follow the links to the VBL Aquarium
documentation for a model to learn more. These models have a `.to_json_string()` method that will convert the model
object to a string that can be sent over Socket.IO.

## Events

Client applications should send messages to these events to interact with the server. The server will respond using
Socket.IO acknowledgements.

### Get Ephys Link Version

| Event         | Input | Response |
|---------------|-------|----------|
| `get_version` | None  | `string` |

[Semantically Versioned](https://semver.org/) number.

__Examples:__

Input: None

Response:

- `"2.0.0"`
- `"2.0.0b2`

### Get Pinpoint ID

| Event             | Input | Response |
|-------------------|-------|----------|
| `get_pinpoint_id` | None  | `string` |

Proxy connection ID (first 8 characters of a UUID v4).

__Example:__

Input: None

Response: `"81f8de08"`

### Get Platform Info

| Event               | Input | Return                                                        |
|---------------------|-------|---------------------------------------------------------------|
| `get_platform_info` | None  | [`PlatformInfo`][vbl_aquarium.models.ephys_link.PlatformInfo] |

__Example:__

Input: N/A

Response:

```json
{
  "Name": "Sensapex uMp-4",
  "CliName": "ump-4",
  "AxesCount": 4,
  "Dimensions": {
    "x": 20.0,
    "y": 20.0,
    "z": 20.0,
    "w": 20.0
  }
}
```

### List Available Manipulators

| Event              | Input | Return                                                                             |
|--------------------|-------|------------------------------------------------------------------------------------|
| `get_manipulators` | None  | [`GetManipulatorResponse`][vbl_aquarium.models.ephys_link.GetManipulatorsResponse] |

__Example:__

Input: N/A

Response:

```json
{
  "Manipulators": [
    "1",
    "2",
    "3"
  ],
  "Error": ""
}
```

```json
{
  "Manipulators": [],
  "Error": "No manipulators found"
}
```

### Get Manipulator Position

| Event          | Input                     | Return                                                                    |
|----------------|---------------------------|---------------------------------------------------------------------------|
| `get_position` | Manipulator ID (`string`) | [`PositionalResponse`][vbl_aquarium.models.ephys_link.PositionalResponse] |

__Example:__

Input:

- "1"
- "A"

Response:

```json
{
  "Position": {
    "x": 12.45,
    "y": 7.89,
    "z": 0.81,
    "w": 8.12
  },
  "Error": ""
}
```

```json
{
  "Position": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "w": 0.0
  },
  "Error": "Unable to Read Manipulator Position"
}
```

## Notes

- In the examples, the error response messages are generic examples. The actual error strings you see will be driven by
  what exceptions are raised by the binding.