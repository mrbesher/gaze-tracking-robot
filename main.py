import argparse
import os
import threading
from time import sleep
import time
import cv2
import customtkinter

from PIL import Image
from helpers.gaze_tracking import GazeTracker, GazeDirection
from helpers.robot_control import RobotController

BLUE_COLOR = '#003366'
DARKBLUE_COLOR = '#032140'

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title('Gaze Robot')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.camera_control = True
        # Init GazeTracker object and open video capture
        self.gt = GazeTracker(num_calibration_frames=200)
        self.cap = cv2.VideoCapture(0)

        while self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        scale_factor = 600 / frame.shape[1]

        width = int(frame.shape[1] * scale_factor)
        height = int(frame.shape[0] * scale_factor)

        img = Image.fromarray(frame)
        self.image = customtkinter.CTkImage(img, size=(width, height))

        self.frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.frame.grid_columnconfigure(0, weight=1)

        self.message_label = customtkinter.CTkLabel(self.frame, text='Initializing', bg_color=BLUE_COLOR)
        self.message_label.grid(row=0, columnspan=3, sticky='ew')

        self.image_label = customtkinter.CTkLabel(self.frame, text='', image=self.image)
        self.image_label.grid(row=1, column=0, columnspan=3)

        self.forward_button = customtkinter.CTkButton(self.frame, text='Forward', fg_color=BLUE_COLOR, hover_color=DARKBLUE_COLOR, command=rc.move_forward)
        self.forward_button.grid(row=2, column=1, padx=20, pady=10)

        self.left_button = customtkinter.CTkButton(self.frame, text='Left', fg_color=BLUE_COLOR, hover_color=DARKBLUE_COLOR, command=rc.turn_left)
        self.left_button.grid(row=3, column=0, padx=20, pady=10)

        self.park_button = customtkinter.CTkButton(self.frame, text='Park', fg_color='darkred', hover_color='#670000')
        self.park_button.grid(row=3, column=1, padx=20, pady=10)

        self.right_button = customtkinter.CTkButton(self.frame, text='Right', fg_color=BLUE_COLOR, hover_color=DARKBLUE_COLOR, command=rc.turn_right)
        self.right_button.grid(row=3, column=2, padx=20, pady=10)

        self.calibrate_button = customtkinter.CTkButton(self.frame, text='Calibrate', fg_color='#d8951a', hover_color='#c07d01', command=self.gt.calibrate)
        self.calibrate_button.grid(row=4, column=0, padx=20, pady=10)

        self.backward_button = customtkinter.CTkButton(self.frame, text='Backward', fg_color=BLUE_COLOR, hover_color=DARKBLUE_COLOR, command=rc.move_backward)
        self.backward_button.grid(row=4, column=1, padx=20, pady=10)

        self.backward_button = customtkinter.CTkButton(self.frame, text='Toggle Control', fg_color='#d8951a', hover_color='#c07d01', command=self.toggle_control)
        self.backward_button.grid(row=4, column=2, padx=20, pady=10)

        # select default frame
        self.frame.grid(row=0, column=1, sticky='nsew')
        
        self.cmd_timestamp = time.time()
        self.frame.after(500, self.update_image)

    def update_image(self):
        if not self.cap.isOpened():
            return

        success, frame = self.cap.read()

        if not success:
            return
        
        self.gt.update(frame)
        annotated_frame = self.gt.get_last_annotated_frame()
        direction = self.gt.get_gaze_direction()

        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        # Flip frame horizontally (selfie)
        cv2.flip(annotated_frame, 1)

        scale_factor = 600 / frame.shape[1]

        width = int(frame.shape[1] * scale_factor)
        height = int(frame.shape[0] * scale_factor)

        # Convert frame to PhotoImage object
        image = customtkinter.CTkImage(Image.fromarray(annotated_frame), size=(width, height))

        self.image_label.configure(image=image)
        self.image_label.image = image
        time_delta = round((time.time() - self.cmd_timestamp) * 1000)

        # Update direction label text and color
        status_text = '[Enabled]' if self.camera_control else '[Disabled]'

        if self.gt.is_calibrating:
            self.message_label.configure(text=f'Calibrating\n{status_text}', bg_color=BLUE_COLOR)
        elif direction == GazeDirection.NO_FACE:
            self.message_label.configure(text=f'No Face\n{status_text}', bg_color='darkred')
        elif direction == GazeDirection.UNKNOWN:
            self.message_label.configure(text=f'Direction: Unknown\n{status_text}', bg_color='#d8951a')
        else:
            self.message_label.configure(text=f'Direction: {direction.name}\n{status_text}', bg_color='green')
            if self.camera_control and time_delta > cmd_duration:
                gaze_control_mapping[direction](duration=cmd_duration)
                self.cmd_timestamp = time.time()

        self.frame.after(10, self.update_image)


    def on_closing(self, *kwargs):
        self.cap.release()
        self.destroy()

    def calibrate_button_event(self):
        self.gt.calibrate()

    def toggle_control(self):
        self.camera_control = not self.camera_control


class DummyRobotController(RobotController):
    def send_command(self, *args, **kwargs):
        pass
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', type=str, help='The IP address of the robot')
    parser.add_argument('--dry-run', action='store_true', help='Do not send commands to the robot')
    parser.add_argument('--cmd-dur', type=int, default=250, help='The duration to apply each command. (ms)')
    args = parser.parse_args()

    cmd_duration = args.cmd_dur

    if args.dry_run:
        rc = DummyRobotController(args.ip)
        print('Dry run: commands will not be sent to the robot')
    else:
        rc = RobotController(args.ip)

    gaze_control_mapping = {
        GazeDirection.UP: rc.move_forward,
        GazeDirection.DOWN: rc.move_backward,
        GazeDirection.RIGHT: rc.turn_right,
        GazeDirection.LEFT: rc.turn_left,
        GazeDirection.CENTER: rc.park_robot,
    }

    app = App()
    app.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.bind('<Escape>', app.on_closing)
    app.mainloop()

