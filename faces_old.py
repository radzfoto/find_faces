# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces
from pathlib import Path
import json
import numpy as np
from deepface import DeepFace
import logging
from global_logger import configure_logger
from deepface.detectors import FaceDetector
from deepface.commons import functions
import time
import cv2
from traverser import Traverser

class Faces:

    def __init__(self, params: dict) -> None:

        defaults_json_string = """
        {
            "root_images_dir": null,
            "identification_model_name": "DeepFace",
            "face_detector_model_name": "mtcnn",
            "normalization": "base",
            "grayscale": false,
            "align": true,
            "silent": false,
            "distance_metric": "cosine",
            "use_program_dir_for_logs": false,
            "log_dir": null,
            "log_filename": "faces.log",
            "log_level": null,
            "log_messages_to_console": false,
            "force_early_model_build": false,
            "metadata_dirname": ".faces",
            "metadata_extension": ".json",
            "image_file_types": [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"],
            "debug": false,
            "debug_max_files_to_process": 1000000000,
            "debug_max_faces_to_process": 1000000000,
            "debug_use_deepface_represent": false
        } """
        self.defaults = json.loads(defaults_json_string)

        if self.defaults['root_images_dir'] is None:
            self.defaults['root_images_dir'] = Path().home() / 'pictures'
        if self.defaults['log_dir'] is None:
            self.defaults['log_dir'] = (Path().home() / '.faces').as_posix(),  # Default to user home directory
        if self.defaults['log_level'] is None:
            self.defaults['log_level'] = logging.DEBUG

        self.params: dict = {}
        # Iterate over the default values dictionary.
        for variable_name, default_value in self.defaults.items():
            # Get the value of the variable from the params dict.
            value = params.get(variable_name, default_value)
            self.params[variable_name] = value

        self.root_images_dir = self.params["root_images_dir"]
        self.identification_model_name = self.params["identification_model_name"]
        self.face_detector_model_name = self.params["face_detector_model_name"]
        self.normalization = self.params["normalization"]
        self.grayscale = self.params["grayscale"]
        self.align = self.params["align"]
        self.silent = self.params["silent"]
        self.distance_metric = self.params["distance_metric"]
        self.use_program_dir_for_logs = self.params["use_program_dir_for_logs"]
        self.log_dir = self.params["log_dir"]
        self.log_filename = self.params["log_filename"]
        self.log_level = self.params["log_level"]
        self.log_messages_to_console = self.params["log_messages_to_console"]
        self.force_early_model_build = self.params["force_early_model_build"]
        self.metadata_dirname = self.params["metadata_dirname"]
        self.metadata_extension = self.params["metadata_extension"]
        self.image_file_types = self.params["image_file_types"]
        self.debug = self.params["debug"]
        self.debug_max_files_to_process = self.params["debug_max_files_to_process"]
        self.debug_max_faces_to_process = self.params["debug_max_faces_to_process"]
        self.debug_use_deepface_represent = self.params["debug_use_deepface_represent"]

        self.root_images_dir: Path = Path(self.root_images_dir)
        if not self.root_images_dir.is_absolute():
            self.root_images_dir = Path.home() / self.root_images_dir
        assert self.root_images_dir.exists(), \
            f'Pictures directory {self.root_images_dir.as_posix()} does not exist.'
        
        if self.use_program_dir_for_logs:
            # overrides default of using home dir or any other assigned log_dir value
            self.log_dir: Path = Path(__file__).parent
        if self.debug:
            self.log_level: int = logging.DEBUG

        self.image_file_types_glob: str = '|'.join(f'*{ext}' for ext in self.image_file_types)

        # from DeepFace
        self.identification_model_names: list[str] = [
            'VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID',
            'Dlib', 'ArcFace', 'SFace']
        identify_string: str = ", ".join(string for string in self.identification_model_names)
        assert self.identification_model_name in self.identification_model_names, \
            f'Invalid face identification model: {self.identification_model_name}. Valid values are {identify_string}'

        # from DeepFace functions
        self.face_detectors: list[str] = [
            'opencv',
            'ssd',
            'dlib',
            'mtcnn',
            'retinaface',
            'mediapipe',
            'yolov8',
            'yunet']
        detect_string: str = ", ".join(string for string in self.face_detectors)
        assert self.face_detector_model_name in self.face_detectors, \
            f'Invalid face identification model: {self.face_detector_model_name}. Valid values are {detect_string}'
                        
        # from DeepFace functions
        self.normalizations: list[str] = ['base', 'raw', 'Facenet', 'Facenet2018', 'VGGFace', 'VGGFace2', 'ArcFace']
        norms_string: str = ", ".join(string for string in self.normalizations)
        assert self.normalization in self.normalizations, \
            f'Invalid face identification model: {self.normalizations}. Valid values are {norms_string}'

        self.log: logging.Logger = configure_logger(log_name='faces_logger',
                         log_file=self.log_dir / self.log_filename,
                         log_level=self.log_level,
                         log_messages_to_console=self.log_messages_to_console)

        self.log.info('\n\n---------- Starting FACES ----------------------------------------------------\n\n')
        self.enforce_detection: bool = False
        self.face_detector_model = None
        self.identification_model = None
        if self.force_early_model_build:
            self.face_detector_model = self.get_face_detector_model()
            self.identification_model = self.get_identification_model()
        self.target_size: tuple[int,int] = functions.find_target_size(model_name=self.identification_model_name)
        if self.face_detector_model_name not in self.face_detectors:
            error_msg: str = f'Invalid face detector backend: {self.face_detector_model_name}'
            self.log.error(error_msg)
            raise ValueError(error_msg)
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
                           is_normalized: bool = True):
        if is_normalized:
             norm_image = image
        else:
            norm_image = functions.normalize_input(img=image, normalization=self.normalization)

        # represent
        self.identification_model = self.get_identification_model()
        if 'keras' in str(type(self.identification_model)):
            # new tf versions show progress bar, set verbose=0 if annoying, 1 for one progress bar, 2 for one bar per epoch
            embedding = self.identification_model.predict(norm_image, verbose=2)[0].tolist()
        else:
            # SFace and Dlib are not keras models and no verbose arguments
            embedding = self.identification_model.predict(norm_image)[0].tolist()

        return embedding
    # end get_representation()

    @classmethod
    def get_from_image(cls, image: np.ndarray, area: dict[str, int]) -> np.ndarray:
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        return image[y:y+h, x:x+w]
    # end get_from_image

    def resize_to_target(self, image: np.ndarray, is_normalized=True) -> np.ndarray:
        if is_normalized:
            norm_image = image
        else:
            norm_image = functions.normalize_input(img=image, normalization=self.normalization)

        # Get the dimensions of the image
        h, w = norm_image.shape[:2]

        # Determine the longer dimension to use for both dimensions of the square image
        max_dim = max(h, w)

        # Calculate padding values
        pad_h = (max_dim - h) // 2
        pad_w = (max_dim - w) // 2

        # Pad the image to make it square
        square_image = cv2.copyMakeBorder(norm_image, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        # Resize the image to the desired dimensions
        resized_image = cv2.resize(square_image, self.target_size)
        return resized_image
    # end resize_to_target()

    def get_from_imagefile(self, filepath: Path) -> list[dict]:
        self.log.info(f'Finding faces from image: {str(filepath)}\n')
        start_time = time.time()
        if self.debug_use_deepface_represent:
            self.log.info(f'Starting DeepFace.represent at time: {start_time}')
            faces: list[dict] = DeepFace.represent(
                            img_path=filepath.as_posix(),
                            enforce_detection=self.enforce_detection,
                            model_name=self.identification_model_name,
                            detector_backend=self.face_detector_model_name,
                            align=self.align,
                            normalization=self.normalization)
            end_time = time.time()
            delta_time = end_time - start_time
            self.log.info(f'Finished DeepFace.represent at time: {end_time} taking: {delta_time} seconds')
            self.log.info(f'Found {len(faces)} face(s) from image {filepath.as_posix()}')
            return faces

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
            embedding = self.get_representation(image = normalized_face_image)
            end_time = time.time()
            delta_time = end_time - start_time
            self.log.info(f'Embedding generated in {delta_time} seconds.')
            face = {'name': None, 'confidence': confidence, 'embedding': embedding}
            face.update(area)
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
            if self.debug and (file_count > self.debug_max_files_to_process):
                break
            fp_faces_found: tuple[Path, list[dict]] = (filepath, self.get_from_imagefile(filepath))
            fp_faces.extend([fp_faces_found])
        # end for
        self.log.info(f'Found {len(fp_faces)} file/face tuples from list of filepaths')
        return fp_faces
    # end get_faces_from_filelist()

    def make_metadata_dir(self, dir_path: Path) -> Path:
        metadata_path = dir_path / self.metadata_dirname
        metadata_path.mkdir(parents=False, exist_ok=True)
        return metadata_path
    # end make_metadata_dir()

    def generate_metadata_filepath_name(self, metadata_dir: Path, image_filepath: Path) -> Path:
        face_filepath = metadata_dir / f'{image_filepath.name}{self.metadata_extension}'
        return face_filepath
    # end generate_metadata_filepath_name()

    @classmethod
    def save_faces(cls, metadata_filepath: Path, faces: list[dict]) -> None:
        json_string: str = json.dumps(faces, indent=4)

        with metadata_filepath.open('w') as md_fp:
            md_fp.write(json_string)
    # end save_faces()

    @classmethod
    def get_saved_faces(cls, metadata_filepath: Path, faces: list[dict]) -> list[dict] | None:
        if not metadata_filepath.exists():
            return None
        with metadata_filepath.open("r") as md_fp:
            faces = json.load(md_fp)
        return faces
    # end get_saved_faces()

    @classmethod
    def is_hidden(cls, path: Path) -> bool:
        return path.name.startswith('.')
    # end is_hidden()

    def find_faces(self, dir_path: Path) -> dict[str, int]:
        self.log.info('\nStarting find faces...\n')
        find_faces_start_time = time.time()

        counts = {'faces': 0, 'files': 0}

        for image_fp in dir_path.iterdir():
            if image_fp.is_dir():
                if not self.is_hidden(image_fp): # Don't traverse hidden directories
                    sub_counts = self.find_faces(image_fp)
                    counts['faces'] += sub_counts['faces']
                    counts['files'] += sub_counts['files']
            elif image_fp.is_file():
                if str(image_fp.suffix).lower() in self.image_file_types:
                    face_filepath: Path = self.generate_metadata_filepath_name(dir_path / self.metadata_dirname, image_fp)
                    if not face_filepath.exists(): # If exists, faces were already found in an earlier run
                        new_faces = self.get_from_imagefile(image_fp)
                        if len(new_faces) > 0:
                            self.make_metadata_dir(dir_path)
                            Faces.save_faces(face_filepath, new_faces)
                            counts['faces'] += len(new_faces)
                        counts['files'] += 1
                        if self.debug and ((counts['files'] >= self.debug_max_files_to_process) or (counts['faces'] >= self.debug_max_faces_to_process)):
                            break
                        # end if
                    # end if
                # end if
            else:
                # Not a file or directory, so skip whatever it is
                pass
            #end if
        # end for
        find_faces_end_time = time.time()
        find_faces_run_time = find_faces_end_time - find_faces_start_time
        self.log.info(f"Found {counts['faces']} new face(s) from {counts['files']} new file(s) in {find_faces_run_time} seconds.\n")
        return counts
    # end find_faces

    def view_faces_in_image(self, image_path: Path, metadata_path: Path) -> None:
        return

    def view_faces(self, dir_path: Path) -> dict[str, int]:
        self.log.info('\nStart view faces...\n')
        view_faces_start_time: float = time.time()

        dirs = Traverser(dir_path, is_dir_iterator=True)

        counts: dict[str, int] = {'faces': 0, 'files': 0}

        for dir in dirs:
            metadata_path: Path = dir / self.metadata_dirname
            if metadata_path.exists():
                for metadata_fp in [file for file in metadata_path.iterdir() if file.is_file() and file.suffix == '.json']:
                    image_path: Path = metadata_path.parent / Path(metadata_fp.name).stem
                    if not image_path.exists():
                        # The image file that corresponds to this metadata must have been deleted, so remove the metadata associated with that file
                        metadata_fp.unlink()
                    else:
                        self.log.info(f'Viewing faces in image: {image_path.as_posix()}')
                        self.view_faces_in_image(image_path, metadata_fp)
                        counts['files'] += 1
            #end if
        # end for
        view_faces_end_time: float = time.time()
        view_faces_run_time: float = view_faces_end_time - view_faces_start_time
        self.log.info(f"Viewed {counts['faces']} face(s) from {counts['files']} file(s) in {view_faces_run_time} seconds.\n")
        return counts
    # end view_faces

    def identify_faces(self, dir_path: Path) -> dict[str, int]:
        self.log.info('\nStarting identify faces...\n')
        identify_faces_start_time = time.time()

        counts = {'faces': 0, 'files': 0}

        identify_faces_end_time = time.time()
        identify_faces_run_time = identify_faces_end_time - identify_faces_start_time
        self.log.info(f"Identified {counts['faces']} new face(s) from {counts['files']} new file(s) in {identify_faces_run_time} seconds.\n")
        return counts
    # end identify_faces

    def find(self):
        self.find_faces(self.root_images_dir)
    # end find()

    def identify(self) -> None:
        self.identify_faces(self.root_images_dir)
        pass
    # end identify

# end class Faces

def main():
    operating_parameters_filename: str = 'faces_parameters.json'

    operating_parameters_path = Path(__file__).parent / operating_parameters_filename
    with operating_parameters_path.open('r') as params_file:
        params = json.load(params_file)

    faces: Faces = Faces(params)

    faces.find()

    faces.identify()

    faces.close()
    return
# end main

if __name__ == '__main__':
    main()


