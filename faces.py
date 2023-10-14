# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces
import platform
from pathlib import Path
import json
import numpy as np
from deepface import DeepFace
from global_logger import Global_logger
#import utilities as util
from deepface.detectors import FaceDetector
from deepface.commons import functions
#import pandas as pd
import time
import cv2

class Faces:

    debug: bool = True
    debug_max_files_to_process = 30
    debug_max_faces_to_process = 40
    debug_use_deepface_represent = False
    debug_use_detect_faces = True

    metadata_dirname: str = '.faces'
    metadata_extension: str = '.faces'

    image_file_types = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']

    # from DeepFace
    model_names: list[str] = [
        'VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID',
        'Dlib', 'ArcFace', 'SFace']

    # from DeepFace functions
    face_detectors = [
        'opencv',
        'ssd',
        'dlib',
        'mtcnn',
        'retinaface',
        'mediapipe',
        'yolov8',
        'yunet']
                 
    # from DeepFace functions
    normalizations: str = ['base', 'raw', 'Facenet', 'Facenet2018', 'VGGFace', 'VGGFace2', 'ArcFace']

    def __init__(self, identification_model_name: str = 'DeepFace',
                 face_detector_model_name: str = 'mtcnn',
                 normalization: str = 'base',
                 align: bool = True,
                 enforce_detection: bool = False,
                 grayscale: bool = False,
                 silent: bool = False,
                 distance_metric: str = 'cosine',
                 log_dir: Path = None,
                 log_filename: str = '.faces.log',
                 log_messages = Global_logger.INFO,
                 log_messages_to_console = True,
                 force_early_model_build = False):

        if Faces.debug:
            force_early_model_build = True
            default_log_messages = Global_logger.DEBUG
        else:
            default_log_messages = log_messages

        self.logger_config = Global_logger(root_dir=log_dir, filename=log_filename,
                                           log_messages=default_log_messages,
                                           log_messages_to_console=log_messages_to_console)
        self.log = self.logger_config.global_logger

        self.log.info('\n\n---------- Starting FACES ----------------------------------------------------\n\n')

        self.identification_model_name = identification_model_name
        self.face_detector_model_name = face_detector_model_name  # DeepFace calls this detector_backend
        self.face_detector_model = None
        self.identification_model = None
        if force_early_model_build:
            self.face_detector_model = self.get_face_detector_model()
            self.identification_model = self.get_identification_model()
        self.target_size: tuple[int,int] = functions.find_target_size(model_name=identification_model_name)
        if face_detector_model_name not in Faces.face_detectors:
            error_msg: str = f'Invalid face detector backend: {face_detector_model_name}'
            self.log.error(error_msg)
            raise ValueError(error_msg)
        self.normalization = normalization
        self.align = align
        self.enforce_detection = enforce_detection
        self.grayscale = grayscale
        self.silent: bool = silent
        self.distance_metric: str = distance_metric
    # end __init__

    def close(self):
        self.log.info('\n\n---------- FACES ended ----------------------------------------------------\n')
    # end close()

    def get_face_detector_model(self): # Lazy model build
        if self.face_detector_model is None:
            self.log.info(f'Face detection model build starting: {self.face_detector_model_name}...')
            start_time = time.time()
            self.face_detector_model = FaceDetector.build_model(self.face_detector_model_name)
            end_time = time.time()
            self.log.info(f'Face detection model built in {end_time - start_time} seconds.\n')
        return self.face_detector_model
    # end get_face_detector_model

    def get_identification_model(self): # Lazy model build
        if self.identification_model is None:
            self.log.info(f'Identification model build starting: {self.identification_model_name}...')
            start_time = time.time()
            self.identification_model = DeepFace.build_model(self.identification_model_name)
            end_time = time.time()
            self.log.info(f'Identification model built {end_time - start_time} seconds.\n')
        return self.identification_model
#    end get_identification_model

    def get_representation(self,
                           image: np.ndarray,
                           is_normalized: bool = False):
        if not is_normalized:
            img = functions.normalize_input(img=image, normalization=self.normalization)

        # represent
        self.identification_model = self.get_identification_model()
        if 'keras' in str(type(self.identification_model)):
            # new tf versions show progress bar, set verbose=0 if annoying, 1 for one progress bar, 2 for one bar per epoch
            embedding = self.identification_model.predict(image, verbose=2)[0].tolist()
        else:
            # SFace and Dlib are not keras models and no verbose arguments
            embedding = self.identification_model.predict(image)[0].tolist()

        return embedding
    # end get_representation()

    @classmethod
    def get_from_image(cls, image: np.ndarray, area: dict[str, int]) -> np.ndarray:
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        return image[y:y+h, x:x+w]
    # end get_from_image

    def resize_to_target(self, image: np.ndarray) -> np.ndarray:
        # Get the dimensions of the image
        h, w = image.shape[:2]

        # Determine the longer dimension to use for both dimensions of the square image
        max_dim = max(h, w)

        # Calculate padding values
        pad_h = (max_dim - h) // 2
        pad_w = (max_dim - w) // 2

        # Pad the image to make it square
        square_image = cv2.copyMakeBorder(image, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        # Resize the image to the desired dimensions
        resized_image = cv2.resize(square_image, self.target_size)
        return resized_image
    # end resize_to_target()

    def get_from_imagefile(self,
                               filepath: Path) -> list[dict]:
        self.log.info(f'Finding faces from image: {str(filepath)}\n')
        if Faces.debug_use_deepface_represent:
            start_time = time.time()
            self.log.info(f'Starting DeepFace.represent at time: {start_time}')
            faces: list[dict] = DeepFace.represent(
                            img_path=filepath.as_posix(),
                            model_name=self.identification_model_name,
                            enforce_detection=self.enforce_detection,
                            face_detector_model_name=self.face_detector_model_name,
                            align=self.align,
                            normalization=self.normalization)
            end_time = time.time()
            delta_time = end_time - start_time
            self.log.info(f'Finished DeepFace.represent at time: {end_time} taking: {delta_time} seconds')
            self.log.info(f'Found {len(faces)} face(s) from image {filepath.as_posix()}')
            return faces
        start_time = time.time()
        if self.debug_use_detect_faces:
            image = cv2.imread(filepath.as_posix())
            if image is None:
                err_msg = f'Unable to open image file: {filepath.as_posix()}'
                self.log.critical(err_msg)
                raise FileExistsError(err_msg)
            faces_found: list = FaceDetector.detect_faces(face_detector=self.get_face_detector_model(), 
                                                          detector_backend=self.face_detector_model_name, 
                                                          img=image, 
                                                          align=self.align)
        else:
            faces_found = functions.extract_faces(
                        img=filepath.as_posix(),
                        target_size=self.target_size,
                        detector_backend=self.face_detector_model_name,
                        enforce_detection=self.enforce_detection,
                        align=self.align,
                        grayscale=self.grayscale)
        end_time = time.time()
        delta_time = end_time - start_time
        face_count = len(faces_found)
        self.log.info(f'Found {len(faces_found)} face(s) in {delta_time} seconds from image {filepath.as_posix()}')
        faces: list[dict] = []
        face_count = 0
        embeddings_start_time = time.time()
        for normalized_face_image, area, confidence in faces_found:
            self.log.info(f'Generating embedding for face: {face_count}')
            start_time = time.time()
            embedding = self.get_representation(image = normalized_face_image,
                                                is_normalized = True)
            end_time = time.time()
            delta_time = end_time - start_time
            self.log.info(f'Embedding generated in {delta_time} seconds.')
            face = {'name': None, 'confidence': confidence, 'embedding': embedding}
            if self.debug_use_detect_faces:
                region: dict[str, int] = {'x': int(area[0]), 'y': int(area[1]), 'w': int(area[2]), 'h': int(area[3])}
            else:
                region: dict[str, int] = area
            face.update(region)
            faces.append(face)
            face_count += 1
        # end for
        end_time = time.time()
        delta_time = end_time - embeddings_start_time
        self.log.info(f'Embeddings for {face_count} face(s) generated in {delta_time} seconds.\n')
        return faces
    # end get_from_imagefile

    def get_from_filelist(self, filepaths: list[Path]) -> list[tuple[Path, list[dict]]]:
        fp_faces: list[tuple[Path, list[dict]]] = []
        for file_count, filepath in enumerate(filepaths):
            if Faces.debug and (file_count > Faces.debug_max_files_to_process):
                break
            fp_faces_found: tuple[Path, list[dict]] = (filepath, self.get_from_imagefile(filepath))
            fp_faces.extend(fp_faces_found)
        # end for
        self.log.info(f'Found {len(fp_faces)} file/face tuples from list of filepaths')
        return fp_faces
    # end get_faces_from_filelist()

    @classmethod
    def make_metadata_dir(cls, dir_path: Path) -> Path:
        metadata_path = dir_path / Faces.metadata_dirname
        if not metadata_path.exists():
            metadata_path.mkdir(parents=False)
        return metadata_path
    # end make_metadata_dir()

    @classmethod
    def generate_metadata_filepath_name(cls, metadata_dir: Path, image_filepath: Path) -> Path:
        face_filepath = metadata_dir / f'{image_filepath.name}{Faces.metadata_extension}'
        return face_filepath
    # end generate_metadata_filepath_name

    @classmethod
    def save_faces(cls, metadata_filepath: Path, faces: list[dict]) -> None:
        json_string: str = json.dumps(faces, indent=4)

        with metadata_filepath.open('w') as md_fp:
            md_fp.write(json_string)
    # end save_faces

    @classmethod
    def get_saved_faces(cls, metadata_filepath: Path, faces: list[dict]) -> list[dict]:
        if not metadata_filepath.exists():
            return None
        with metadata_filepath.open("r") as md_fp:
            faces = json.load(md_fp)
        return faces
    # end get_saved_faces

    @classmethod
    def is_hidden(cls, path: Path) -> bool:
        return path.name.startswith('.')
    # end is_hidden()

    def find(self, dir_path: Path, timeit = False) -> dict[str, int]:
        self.log.info('\nStarting find faces...\n')
        if timeit:
            find_faces_start_time = time.time()

        metadata_dir: Path = Faces.make_metadata_dir(dir_path)
        counts = {'faces': 0, 'files': 0}

        for image_fp in dir_path.iterdir():
            if image_fp.is_dir():
                if not Faces.is_hidden(image_fp): # Don't traverse hidden directories
                    sub_counts = self.find(image_fp)
                    counts['faces'] += sub_counts['faces']
                    counts['files'] += sub_counts['files']
            elif image_fp.is_file():
                if image_fp.suffix in Faces.image_file_types:
                    face_filepath: Path = Faces.generate_metadata_filepath_name(metadata_dir, image_fp)
                    if not face_filepath.exists(): # If exists, faces were already found
                        new_faces = self.get_from_imagefile(image_fp)
                        Faces.save_faces(face_filepath, new_faces)
                        counts['files'] += 1
                        counts['faces'] += len(new_faces)
                        if Faces.debug and ((counts['files'] >= Faces.debug_max_files_to_process) or (counts['faces'] >= Faces.debug_max_faces_to_process)):
                            break
                        # end if
                    # end if
                # end if
            else:
                # Not a file or directory, so skip whatever it is
                pass
            #end if
        # end for
        if timeit:
            find_faces_end_time = time.time()
            find_faces_run_time = find_faces_end_time - find_faces_start_time
        else:
            find_faces_run_time = 'time not measured'
        self.log.info(f"Found {counts['faces']} new face(s) from {counts['files']} new file(s) in {find_faces_run_time} seconds.\n")
        return counts
    # end find

    def identify(self, dir_path:Path) -> None:
        pass
    # end identify

# end class Faces

def main():
    if 'arm64' in platform.platform():
        root_dir: Path = Path("/Users/raul/Pictures/test/test_small")
    else:
        root_dir: Path = Path("/home/raul/raul/test/test_small")
    
    log_dir: Path = root_dir

    assert root_dir.is_absolute(), 'Error: Source and database paths must be absolute paths.'

    faces: Faces = Faces(log_dir=log_dir)

    faces.find(root_dir, timeit=True)

    faces.close()
    return
# end main

if __name__ == '__main__':
    main()


