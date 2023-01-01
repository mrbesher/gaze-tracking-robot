import requests

class RobotController:
    def __init__(self, ip_address):
        """Initializes a new instance of the RobotController class.

        Args:
            ip_address (str): The IP address of the robot.
        """
        self.ip_address = ip_address

    def send_command(self, command, duration=1000, velocity=150):
        """Sends a command to the robot to execute.

        Args:
            command (str): The command to send to the robot. Must be one of the following:
                'MF' (move forward), 'MB' (move backward), 'TL' (turn left), 'TR' (turn right),
                'P' (park).
            duration (int, optional): The duration in milliseconds to execute the command. Defaults to 1000.
            velocity (int, optional): The velocity at which to execute the command. Defaults to 150.
        """
        url = f'http://{self.ip_address}'
        params = {
            'cmd': command,
            'dur': duration,
            'vel': velocity
        }
        requests.get(url, params=params)
