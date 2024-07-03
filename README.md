# Turck Python Library

This library provides a Python interface for interacting with the Turck Modules (Curently only FEN20-16DXP I/O module ) using Modbus TCP communication.

## Installation

You can install this library by cloning the repository and running the following command:

```bash
pip install -e .
```

## Usage

Here's a basic example of how to use the library:

```python
from turck_py.FEN20_16DXP import FEN20_16DXP
import time

# Create an instance of FEN20_16DXP
controller = FEN20_16DXP(host="192.168.1.11", port=502)  # Replace with your device's IP and port

# Start the connection
controller.start_connection()

# Read all inputs
inputs = controller.get_inputs()
print("Current input states:", inputs)

# Set multiple outputs
new_outputs = {0: True, 1: False, 2: True}
controller.set_outputs(new_outputs)

# Read outputs
outputs = controller.get_outputs()
print("Current output states:", outputs)
```

## Features
- Connect to and communicate with Turck FEN20-16DXP I/O module
- Read input states
- Read and set output states
- Get device status and diagnostics
- Supports both synchronous and asynchronous operations


## API Reference
### FEN20_16DXP
- start_connection(): Establishes connection with the device
- is_connected(): Checks if the connection is active
- get_inputs(): Reads all input states
- get_input(input: int): Reads state of a specific input
- get_outputs(): Reads all output states
- get_output(output: int): Reads state of a specific output
- set_outputs(outputs: dict): Sets multiple outputs
- set_output(output: int, value: bool): Sets a specific output
- get_status(): Gets device status
- get_diagnostics(): Gets device diagnostics
- get_io_diagnostics(): Gets I/O diagnostics

### FEN20_16DXP_async
- Provides the same functionality as FEN20_16DXP but with asynchronous methods for use with asyncio.

## Requirements
Python 3.6+
pymodbus

## License
MIT License

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

