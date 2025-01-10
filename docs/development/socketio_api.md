# Socket.IO API

This section documents the [Socket.IO](https://socket.io/) API. The document is intended for developers building client
applications communicating with the server. If you are looking for information on how to set up and run the server, see
the [installation guide](../home/installation.md)!

## Data Types

All messages on Socket.IO are passed as strings. Complex data structures are JSON encoded, converted to strings, and
then sent. These structures have their JSON schemas documented
on [VBL Aquarium](https://github.com/VirtualBrainLab/vbl-aquarium/tree/main/models/schemas/ephys_link).

This documentation will reference the Pydantic versions of these models as they are extensively documented. For most
functions, their functions and responses are documented by these models. Follow the links to the VBL Aquarium
documentation for a model to learn more. These models have a `.to_json_string()` method that will convert the model
object to a string that can be sent over Socket.IO.

## Events

Client applications should send messages to these events to interact with the server. The server will respond using
[Socket.IO acknowledgments](https://socket.io/docs/v4/#acknowledgements).

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

__Examples:__

Input: N/A

Response:

- Normal:

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

- Error:

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

__Examples:__

Input:

- `"1"`
- `"A"`

Response:

- Normal:

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

- Error:

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

### Get Manipulator Angles

| Event        | Input                     | Return                                                              |
|--------------|---------------------------|---------------------------------------------------------------------|
| `get_angles` | Manipulator ID (`string`) | [`AngularResponse`][vbl_aquarium.models.ephys_link.AngularResponse] |

__Examples:__

Input:

- `"1"`
- `"A"`

Response:

- Normal:

```json
    {
  "Angles": {
    "x": 45.0,
    "y": 0.0,
    "z": 90.0
  },
  "Error": ""
}
```

- Error:

```json
  {
  "Angles": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
  },
  "Error": "Unable to Read Manipulator Angles"
}

```

### Get Probe Shank Count

| Event             | Input                     | Return                                                                    |
|-------------------|---------------------------|---------------------------------------------------------------------------|
| `get_shank_count` | Manipulator ID (`string`) | [`ShankCountResponse`][vbl_aquarium.models.ephys_link.ShankCountResponse] |

__Examples:__

Input:

- `"1"`
- `"A"`

Response:

- Normal:

```json
{
  "ShankCount": 3,
  "Error": ""
}
```

- Error:

```json
{
  "ShankCount": 1,
  "Error": "Unable to Read Probe Shank Count"
}
```

### Set Manipulator Position

| Event          | Input                                                                     | Return                                                                    |
|----------------|---------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `set_position` | [`SetPositionRequest`][vbl_aquarium.models.ephys_link.SetPositionRequest] | [`PositionalResponse`][vbl_aquarium.models.ephys_link.PositionalResponse] |

__Examples:__

Input:

```json
{
  "ManipulatorId": "1",
  "Position": {
    "x": 1.5,
    "y": 2.0,
    "z": 0.0,
    "w": 0.84
  },
  "Speed": 0.05
}
```

Response:

- Normal:

```json
{
  "Position": {
    "x": 1.5,
    "y": 2.0,
    "z": 0.0,
    "w": 0.84
  },
  "Error": ""
}
```

- Manipulator is set to be inside the brain (position setting is disallowed):

```json
{
  "Position": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "w": 0.0
  },
  "Error": "Can not move manipulator while inside the brain. Set the depth (\"set_depth\") instead."
}
```

- The manipulator did not make it to the final destination. This is not necessarily unintentional. This response is
  produced
  if a movement is stopped.

```json
{
  "Position": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "w": 0.0
  },
  "Error": "Manipulator 1 did not reach target position on axis x. Requests: 1.5, got: 0.82."
}
```

### Set Manipulator Depth

| Event       | Input                                                               | Return                                                                |
|-------------|---------------------------------------------------------------------|-----------------------------------------------------------------------|
| `set_depth` | [`SetDepthRequest`][vbl_aquarium.models.ephys_link.SetDepthRequest] | [`SetDepthResponse`][vbl_aquarium.models.ephys_link.SetDepthResponse] |

__Examples:__

Input:

```json
{
  "ManipulatorId": "1",
  "Depth": 1.7,
  "Speed": 0.005
}
```

Response:

- Normal:

```json
{
  "Depth": 1.7,
  "Error": ""
}
```

- The manipulator did not make it to the final destination. This is not necessarily unintentional. This response is
  produced
  if a drive is stopped.

```json
{
  "Depth": 0,
  "Error": "Manipulator 1 did not reach target depth. Requested: 1.7, got: 0.6."
}
```

### Set Manipulator to be Inside the Brain

| Event              | Input                                                                           | Return                                                                        |
|--------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `set_inside_brain` | [`SetInsideBrainRequest`][vbl_aquarium.models.ephys_link.SetInsideBrainRequest] | [`BooleanStateResponse`][vbl_aquarium.models.ephys_link.BooleanStateResponse] |

__Examples:__

Input:

```json
{
  "ManipulatorId": "1",
  "Inside": true
}
```

Response:

- Normal:

```json
{
  "State": true,
  "Error": ""
}
```

- Error

```json
{
  "State": false,
  "Error": "Unable to complete operation."
}
```

### Stop a Manipulator's movement

| Event  | Input                     | Return                   |
|--------|---------------------------|--------------------------|
| `stop` | Manipulator ID (`string`) | Error Message (`string`) |

__Examples:__

Input:

- "1"
- "A"

Response:

- Normal: `""`
- Error: `"Unable to stop manipulator."`

### Stop All Manipulators

| Event      | Input | Return                   |
|------------|-------|--------------------------|
| `stop_all` | None  | Error Message (`string`) |

__Examples:__

Input: None

Response:

- Normal: `""`
- Error: `"Unable to stop manipulator."`

### Unknown Event (Error)

Response: `{"error", "Unknown event."}`

## Notes

- In the examples, the error response messages are generic examples. The actual error strings you see will be driven by
  what exceptions are raised by the binding.