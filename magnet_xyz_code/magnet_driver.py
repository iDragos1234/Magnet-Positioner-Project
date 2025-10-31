"""
Author: b-vanstraaten
Date: 20/02/2025
"""
from http.client import responses

import serial
from time import sleep
import serial.tools.list_ports
from qcodes import Instrument
from qcodes import validators as vals
from functools import partial

def convert_to_steps(x, mm_per_step, sign = 1):
    return int(x / mm_per_step) * sign

def convert_to_mm(x, mm_per_step, sign = 1):
    return float(x) * mm_per_step * sign



x_deg_per_step = 0.9
y_deg_per_step = 0.9
z_deg_per_step = 1.8

x_mm_per_turn = 2.0
y_mm_per_turn = 2.0
z_mm_per_turn = 2.0

x_mm_per_step = x_deg_per_step * x_mm_per_turn / 360
y_mm_per_step = y_deg_per_step * y_mm_per_turn / 360
z_mm_per_step = z_deg_per_step * z_mm_per_turn / 360

set_parsers = {
    'x': partial(convert_to_steps, mm_per_step=x_mm_per_step, sign = -1),
    'y': partial(convert_to_steps, mm_per_step=y_mm_per_step, sign = -1),
    'z': partial(convert_to_steps, mm_per_step=z_mm_per_step, sign = -1)
}

get_parsers = {
    'x': partial(convert_to_mm, mm_per_step=x_mm_per_step, sign = -1),
    'y': partial(convert_to_mm, mm_per_step=y_mm_per_step, sign = -1),
    'z': partial(convert_to_mm, mm_per_step=z_mm_per_step, sign = -1)
}

safety_distance = 5
bounds = {
    'x': (-255, 255),
    'y': (-60, 60),
    'z': (0, 555-safety_distance)
}

def list_serial_ports():
    """
    Lists available serial ports.
    Returns:
        list: A list of available serial ports.
    """
    ports = serial.tools.list_ports.comports()
    available_ports = []

    for port, desc, hwid in ports:
        available_ports.append(port)
        print(f"Port: {port} | Description: {desc} | HWID: {hwid}")

    if not available_ports:
        print("No serial ports found.")
    return available_ports


class ArduinoSerial(Instrument):
    """
    QCoDeS Instrument Driver for an Arduino over Serial Communication.
    """

    def __init__(self, name: str, port: str, baudrate: int = 9600, timeout: float = 1, **kwargs):
        """
        Initialise the Arduino serial driver.

        Args:
            name (str): Name of the instrument instance.
            port (str): Serial port for communication.
            baudrate (int): Baud rate for serial communication.
            timeout (float): Timeout for serial reads.
        """
        super().__init__(name, **kwargs)

        if port is None:
            list_serial_ports()
            raise ValueError("No port specified. Use list_serial_ports() to find available ports.")

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        # Establish connection
        self.connection = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        sleep(2)  # Allow time for connection to establish
        print("Arduino initialised.")
        print(f"Connected to {self.port} at {self.baudrate} baud.")

        # Add LED control parameter
        self.add_parameter(
            name="LED",
            label="LED",
            get_cmd="L?",  # Query LED state
            set_cmd="L{}",  # Set LED state
            get_parser=int,
        )

        directions  = ["x", "y", "z"]
        current_position = {}

        for direction in directions:
            self.add_parameter(
                name = f'{direction}_step',
                label= f'{direction}_step',
                get_cmd=f"{direction}?",
                set_cmd=f"{direction}{{}}",
                get_parser=int,
            )

            set_parser = set_parsers[direction]
            get_parser = get_parsers[direction]

            self.add_parameter(
                name = f'{direction}',
                label= f'{direction}',
                get_cmd=f"{direction}?",
                set_cmd=f"{direction}{{}}",
                get_parser=get_parser,
                set_parser=set_parser,
                vals=vals.Numbers(*bounds[direction])
            )

        print('Current position:', self.position())

    def tare(self, coordinates = 'xyz'):
        for coordinate in coordinates:
            assert coordinate.lower() in ['x', 'y', 'z'], 'Invalid coordinate'
            self.ask(f't{coordinate.lower()}')


    def position(self, position = None):
        """
        Get the current position of the magnet.

        Returns:
            dict: The current position of the magnet.
        """
        position = {}
        for direction in ["x", "y", "z"]:
            position[direction] = getattr(self, direction).get()
        return position

    def ask(self, command: str):
        """
        Send a command to the Arduino and return the response.

        Args:
            command (str): The command string to send.

        Returns:
            str: The response from the Arduino.
        """
        return self.write(command)


    def write(self, command: str):
        """
        Send a command to the Arduino.

        Args:
            command (str): The command string to send.
        """
        if not self.connection.is_open:
            raise ConnectionError("Serial connection is not open.")

        self.connection.write(command.encode())

        message = ''
        while message == '':
            message = self.connection.readline().decode().strip()
            sleep(1e-2)
        return message

    def close(self):
        """
        Closes the serial connection.
        """
        if self.connection.is_open:
            self.connection.close()
            print(f"Connection to {self.port} closed.")

    def __del__(self):
        """Ensures proper cleanup on deletion."""
        self.close()


if __name__ == '__main__':
    menno = ArduinoSerial("arduino", "COM10")