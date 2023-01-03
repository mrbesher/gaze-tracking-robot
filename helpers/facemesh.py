import cv2
import numpy as np
import mediapipe as mp

from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions.drawing_utils import DrawingSpec

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

IRIS_BGR = (0, 139, 69)


def get_default_face_mesh_iris_connections_style():
    face_mesh_iris_connections_style = {}
    left_spec = DrawingSpec(color=IRIS_BGR, thickness=2)
    for connection in face_mesh_connections.FACEMESH_LEFT_IRIS:
        face_mesh_iris_connections_style[connection] = left_spec
    right_spec = DrawingSpec(color=IRIS_BGR, thickness=2)
    for connection in face_mesh_connections.FACEMESH_RIGHT_IRIS:
        face_mesh_iris_connections_style[connection] = right_spec
    return face_mesh_iris_connections_style


class FaceMesh:
    # Landmarks
    LEFT_TOP = 386
    LEFT_BOTTOM = 374
    LEFT_INNEl_H = 362
    LEFT_OUTEl_H = 263

    RIGHT_TOP = 159
    RIGHT_BOTTOM = 145
    RIGHT_OUTEl_H = 33
    RIGHT_INNEl_H = 133

    LEFT_IRIS_C = 473
    RIGHT_IRIS_C = 468

    MESH_TOP = 10
    MESH_BOTTOM = 152

    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.image = None
        self.face_landmarks = None

    def __entel__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.face_mesh.__exit__(type, value, traceback)

    def _landmark_to_array(self, landmark):
        if type(landmark) is not np.ndarray:
            return np.array([landmark.x, landmark.y, landmark.z])
        return landmark

    def calc_euclidean(self, landmark1, landmark2):
        landmark1 = self._landmark_to_array(landmark1)
        landmark2 = self._landmark_to_array(landmark2)
        return np.linalg.norm(landmark1 - landmark2)

    def set_image(self, image):
        self.image = image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image)
        if results.multi_face_landmarks:
            self.face_landmarks = results.multi_face_landmarks[0]
        else:
            self.face_landmarks = None

    def get_annotated_image(self):
        if self.image is None:
            return None

        image = self.image.copy()
        image.flags.writeable = True
        if self.face_landmarks is None:
            return image

        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=self.face_landmarks,
            connections=mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=get_default_face_mesh_iris_connections_style())

        return image

    def get_distances(self):
        if self.face_landmarks is None:
            return None

        landmarks = self.face_landmarks.landmark

        # use two points for scaling from the outer mesh
        reference_dist = self.calc_euclidean(
            landmarks[self.MESH_TOP], landmarks[self.MESH_BOTTOM])

        l_eyelid_dist = self.calc_euclidean(
            landmarks[self.LEFT_TOP], landmarks[self.LEFT_BOTTOM])
        l_inner_dist = self.calc_euclidean(
            landmarks[self.LEFT_INNEl_H], landmarks[self.LEFT_IRIS_C])
        l_outer_dist = self.calc_euclidean(
            landmarks[self.LEFT_OUTEl_H], landmarks[self.LEFT_IRIS_C])
        l_top_dist = self.calc_euclidean(
            landmarks[self.LEFT_TOP], landmarks[self.LEFT_IRIS_C])
        l_bottom_dist = self.calc_euclidean(
            landmarks[self.LEFT_BOTTOM], landmarks[self.LEFT_IRIS_C])

        r_eyelid_dist = self.calc_euclidean(
            landmarks[self.RIGHT_TOP], landmarks[self.RIGHT_BOTTOM])
        r_inner_dist = self.calc_euclidean(
            landmarks[self.RIGHT_INNEl_H], landmarks[self.RIGHT_IRIS_C])
        r_outer_dist = self.calc_euclidean(
            landmarks[self.RIGHT_OUTEl_H], landmarks[self.RIGHT_IRIS_C])
        r_top_dist = self.calc_euclidean(
            landmarks[self.RIGHT_TOP], landmarks[self.RIGHT_IRIS_C])
        r_bottom_dist = self.calc_euclidean(
            landmarks[self.RIGHT_BOTTOM], landmarks[self.RIGHT_IRIS_C])

        distances = {
            'l_eyelid_dist': l_eyelid_dist,
            'l_inner_dist': l_inner_dist,
            'l_outer_dist': l_outer_dist,
            'l_top_dist': l_top_dist,
            'l_bottom_dist': l_bottom_dist,
            'r_eyelid_dist': r_eyelid_dist,
            'r_inner_dist': r_inner_dist,
            'r_outer_dist': r_outer_dist,
            'r_top_dist': r_top_dist,
            'r_bottom_dist': r_bottom_dist
        }

        # Return the scaled distances
        return {k: dist / reference_dist for k, dist in distances.items()}
