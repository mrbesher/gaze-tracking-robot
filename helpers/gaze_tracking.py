import collections
import statistics

from enum import Enum
from math import isclose
from helpers.facemesh import FaceMesh

def init_distances_dict():
    return {
        'r_eyelid_dist': [],
        'r_inner_dist': [],
        'r_outer_dist': [],
        'r_top_dist': [],
        'r_bottom_dist': [],
        'l_eyelid_dist': [],
        'l_inner_dist': [],
        'l_outer_dist': [],
        'l_top_dist': [],
        'l_bottom_dist': []
    }

def cmp_with_tol(a, b, tol=6e-2):
    if isclose(a, b, rel_tol=tol):
        return 0

    return a - b

class GazeDirection(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    CENTER = 5
    UNKNOWN = 6
    NO_FACE = 7

class GazeTracker:
    def __init__(self, num_calibration_frames: int=20, buffer_size: int=20):
        self.annotated_frame = None
        self.num_calibration_frames = num_calibration_frames
        self.buffer_size = buffer_size
        self.calibration_frame_count = 0
        self.is_calibrating = True
        self.fm = FaceMesh()
        self.distances = init_distances_dict()
        self.median_distances = {}
        self.gaze_buffer = collections.deque(maxlen=buffer_size)

    def _update_calibration(self, frame_distances):
        for k, dist in frame_distances.items():
            self.distances[k].append(dist)
            self.calibration_frame_count += 1

            if self.calibration_frame_count >= self.num_calibration_frames:
                self.median_distances = {distance_name: statistics.median(distance_values)
                                        for distance_name, distance_values in self.distances.items()}
                self.is_calibrating = False
                self.calibration_frame_count = 0
                self.distances = init_distances_dict()


    def update(self, frame):
        """Updates the gaze tracker with a new frame.

        Args:
            frame: a frame from a video stream
        """
        # update the gaze tracker and annotate the frame
        self.fm.set_image(frame)
        self.annotated_frame = self.fm.get_annotated_image()
        frame_distances = self.fm.get_distances()

        if frame_distances is None:
            self.gaze_buffer.append(GazeDirection.NO_FACE)
            return

        if self.is_calibrating:
            self._update_calibration(frame_distances)
            return
        
        # right eye
        if cmp_with_tol(frame_distances['r_inner_dist'], self.median_distances['r_inner_dist'], tol=1e-1) < 0:
            self.gaze_buffer.append(GazeDirection.LEFT)
        elif cmp_with_tol(frame_distances['r_outer_dist'], self.median_distances['r_outer_dist'], tol=1e-1) < 0:
            self.gaze_buffer.append(GazeDirection.RIGHT)
        elif cmp_with_tol(frame_distances['r_eyelid_dist'], self.median_distances['r_eyelid_dist']) < 0 \
            and cmp_with_tol(frame_distances['r_top_dist'], self.median_distances['r_top_dist']) < 0:
            self.gaze_buffer.append(GazeDirection.DOWN)
        elif cmp_with_tol(frame_distances['r_eyelid_dist'], self.median_distances['r_eyelid_dist']) > 0 \
            and cmp_with_tol(frame_distances['r_bottom_dist'], self.median_distances['r_bottom_dist']) > 0:
            self.gaze_buffer.append(GazeDirection.UP)
        else:
            self.gaze_buffer.append(GazeDirection.CENTER)

        # left eye
        if cmp_with_tol(frame_distances['l_outer_dist'], self.median_distances['l_outer_dist'], tol=1e-1) < 0:
            self.gaze_buffer.append(GazeDirection.LEFT)
        elif cmp_with_tol(frame_distances['l_inner_dist'], self.median_distances['l_inner_dist'], tol=1e-1) < 0:
            self.gaze_buffer.append(GazeDirection.RIGHT)
        elif cmp_with_tol(frame_distances['l_eyelid_dist'], self.median_distances['l_eyelid_dist']) < 0 \
            and cmp_with_tol(frame_distances['l_top_dist'], self.median_distances['l_top_dist']) < 0:
            self.gaze_buffer.append(GazeDirection.DOWN)
        elif cmp_with_tol(frame_distances['l_eyelid_dist'], self.median_distances['l_eyelid_dist']) > 0 \
            and cmp_with_tol(frame_distances['l_bottom_dist'], self.median_distances['l_bottom_dist']) > 0:
            self.gaze_buffer.append(GazeDirection.UP)
        else:
            self.gaze_buffer.append(GazeDirection.CENTER)


    def calibrate(self):
        self.is_calibrating = True

    def get_gaze_direction(self):
        """Returns the current gaze direction.

        Returns:
            an instance of GazeDirection
        """
        if self.is_calibrating:
            return GazeDirection.UNKNOWN
        
        if len(self.gaze_buffer) < self.buffer_size:
            return GazeDirection.UNKNOWN

        direction_counts = collections.Counter(self.gaze_buffer)

        mode, occurrence = direction_counts.most_common(1)[0]

        if occurrence < self.buffer_size // 2:
            return GazeDirection.UNKNOWN

        return mode

    def get_last_annotated_frame(self):
        """Returns the last annotated frame.

        Returns:
            an annotated frame (ndarray)
        """
        return self.annotated_frame
