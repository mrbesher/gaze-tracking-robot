from typing import Union
import requests
from enum import Enum

class Command(Enum):
    MF = 'MF'  # move forward
    MB = 'MB'  # move backward
    TL = 'TL'  # turn left
    TR = 'TR'  # turn right
    P = 'P'  # park

class RobotController:
    def __init__(self, ip_address: str):
        """Initializes a new instance of the RobotController class.

        Args:
            ip_address (str): The IP address of the robot.
        """
        self.ip_address = ip_address

    def send_command(self, command: Union[str, Command], duration :int=100, velocity: int=150):
        """Sends a command to the robot to execute.

        Args:
            command (Union[str, Command]): The command to send to the robot. Must be a string or an instance of the
                Command enum.
            duration (int, optional): The duration in milliseconds to execute the command. Defaults to 100.
            velocity (int, optional): The velocity at which to execute the command. Defaults to 150.
        """
        if isinstance(command, Command):
            command = command.value

        url = f'http://{self.ip_address}'
        params = {
            'cmd': command,
            'dur': duration,
            'vel': velocity
        }
        requests.get(url, params=params)

    def move_forward(self, duration: int=100, velocity: int=150):
        self.send_command(Command.MF, duration=duration, velocity=velocity)

    def move_backward(self, duration: int=100, velocity: int=150):
        self.send_command(Command.MB, duration=duration, velocity=velocity)

    def turn_right(self, duration: int=100, velocity: int=150):
        self.send_command(Command.TR, duration=duration, velocity=velocity)

    def turn_left(self, duration: int=100, velocity: int=150):
        self.send_command(Command.TL, duration=duration, velocity=velocity)

    def park_robot(self, duration: int=100, velocity: int=150):
        self.send_command(Command.P, duration=duration, velocity=velocity)
