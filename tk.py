import tkinter
import customtkinter
import cv2

from PIL import Image
from helpers.gaze_tracking import GazeTracker, GazeDirection

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Initialize GazeTracker object
        self.gt = GazeTracker()

        # Open video capture
        self.cap = cv2.VideoCapture(0)

        # Set window title and size
        self.title("Gaze Tracking App")
        self.geometry("700x450")

        # Set grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create frame to hold image
        self.image_frame = customtkinter.CTkFrame(self, bg_color=("white", "white"), corner_radius=0)
        self.image_frame.grid(row=0, column=0, sticky="nsew")

        # Create label to hold image
        self.image_label = customtkinter.CTkLabel(self.image_frame, bg_color=("white", "white"))
        self.image_label.grid(row=0, column=0, sticky="nsew")

        # Create frame to hold buttons
        self.button_frame = customtkinter.CTkFrame(self, bg_color=("white", "white"), corner_radius=0)
        self.button_frame.grid(row=1, column=0, sticky="nsew")

        # Create buttons
        self.calibrate_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Calibrate",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        anchor="w", command=self.calibrate_button_event)
        self.calibrate_button.grid(row=0, column=0, sticky="ew")

        self.disable_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Disable",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.disable_button_event)
        self.disable_button.grid(row=0, column=1, sticky="ew")

        self.move_right_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Move Right",
                                                 fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                 anchor="w", command=self.move_right_button_event)
        self.move_right_button.grid(row=0, column=2, sticky="ew")

        self.move_left_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Move Left",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        anchor="w", command=self.move_left_button_event)
        self.move_left_button.grid(row=0, column=3, sticky="ew")

        self.forward_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Forward",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.forward_button_event)
        self.forward_button.grid(row=0, column=4, sticky="ew")

        self.backward_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Backward",
                                                       fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.backward_button_event)
        self.backward_button.grid(row=0, column=5, sticky="ew")

        self.park_button = customtkinter.CTkButton(self.button_frame, corner_radius=0, height=40, border_spacing=10, text="Park",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.park_button_event)
        self.park_button.grid(row=0, column=6, sticky="ew")

        # Create label to hold direction text
        self.direction_label = customtkinter.CTkLabel(self.image_frame, text="Direction: ", font=customtkinter.CTkFont(size=15, weight="bold"),
                                                     bg_color=("white", "white"))
        self.direction_label.grid(row=1, column=0, sticky="ew")

        # Start update loop
        self.after(0, self.update_loop)

    def update_loop(self):
        # Read frame from video capture
        success, frame = self.cap.read()

        if not success:
            return

        # Update GazeTracker object with new frame
        self.gt.update(frame)

        # Get annotated frame and gaze direction
        annotated_frame = self.gt.get_last_annotated_frame()
        direction = self.gt.get_gaze_direction()

        # Flip frame horizontally
        cv2.flip(annotated_frame, 1)

        # Convert frame to PhotoImage object
        image = customtkinter.CTkImage(Image.fromarray(annotated_frame))

        # Update image label with new image
        self.image_label.image = image

        # Update direction label text and color
        if direction == GazeDirection.NO_FACE:
            self.direction_label.configure(text="Direction: No Face", bg_color=("red", "red"))
        elif direction == GazeDirection.UNKNOWN:
            self.direction_label.configure(text="Direction: Unknown", bg_color=("yellow", "yellow"))
        else:
            self.direction_label.configure(text=f"Direction: {direction.name}", bg_color=("green", "green"))

        # Restart update loop
        self.after(0, self.update_loop)

    def calibrate_button_event(self):
        # Calibrate GazeTracker object
        self.gt.calibrate()

    def disable_button_event(self):
        # Disable GazeTracker object
        self.gt.disable()

    def move_right_button_event(self):
        # Move robot to the right
        pass

    def move_left_button_event(self):
        # Move robot to the left
        pass

    def forward_button_event(self):
        # Move robot forward
        pass

    def backward_button_event(self):
        # Move robot backward
        pass

    def park_button_event(self):
        # Park robot
        pass

# Run app
app = App()
app.mainloop()

