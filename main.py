import os
import threading
from time import sleep
import cv2
import customtkinter

from PIL import Image
from helpers.gaze_tracking import GazeTracker, GazeDirection

TICK_INTERVAL = 1 / 30 # FPS

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title('Gaze Robot')

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Init GazeTracker object and open video capture
        self.gt = GazeTracker()
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

        # create home frame
        self.frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.frame.grid_columnconfigure(0, weight=1)

        self.message_label = customtkinter.CTkLabel(self.frame, text='Initializing', bg_color='#003366')
        self.message_label.grid(row=0, columnspan=3, sticky='ew')

        self.image_label = customtkinter.CTkLabel(self.frame, text='', image=self.image)
        self.image_label.grid(row=1, column=0, columnspan=3)

        self.forward_button = customtkinter.CTkButton(self.frame, text='Forward', fg_color='green', hover_color='darkgreen')
        self.forward_button.grid(row=2, column=1, padx=20, pady=10)

        self.left_button = customtkinter.CTkButton(self.frame, text='Left', fg_color='green', hover_color='darkgreen')
        self.left_button.grid(row=3, column=0, padx=20, pady=10)

        self.park_button = customtkinter.CTkButton(self.frame, text='Park', fg_color='darkred', hover_color='#670000')
        self.park_button.grid(row=3, column=1, padx=20, pady=10)

        self.right_button = customtkinter.CTkButton(self.frame, text='Right', fg_color='green', hover_color='darkgreen')
        self.right_button.grid(row=3, column=2, padx=20, pady=10)

        self.calibrate_button = customtkinter.CTkButton(self.frame, text='Calibrate', fg_color='#d8951a', hover_color='#c07d01')
        self.calibrate_button.grid(row=4, column=0, padx=20, pady=10)

        self.backward_button = customtkinter.CTkButton(self.frame, text='Backward', fg_color='green', hover_color='darkgreen')
        self.backward_button.grid(row=4, column=1, padx=20, pady=10)

        self.backward_button = customtkinter.CTkButton(self.frame, text='Toggle Control', fg_color='#d8951a', hover_color='#c07d01')
        self.backward_button.grid(row=4, column=2, padx=20, pady=10)

        # select default frame
        self.frame.grid(row=0, column=1, sticky='nsew')
        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop)
        self.thread.start()

    def video_loop(self):
        while not self.stop_event.is_set():
            self.update_image()

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

        # Update direction label text and color
        if direction == GazeDirection.NO_FACE:
            self.message_label.configure(text='Direction: No Face', bg_color=('red', 'red'))
        elif direction == GazeDirection.UNKNOWN:
            self.message_label.configure(text='Direction: Unknown', bg_color=('#d8951a', '#d8951a'))
        else:
            self.message_label.configure(text=f'Direction: {direction.name}', bg_color=('green', 'green'))

    def on_closing(self, *kwargs):
        self.stop_event.set()
        self.cap.release()
        self.thread.join()
        self.destroy()

if __name__ == '__main__':
    app = App()
    app.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.bind('<Escape>', app.on_closing)
    app.mainloop()

