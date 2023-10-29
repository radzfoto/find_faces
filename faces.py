# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces
from pathlib import Path
import json
import time
import logging
import numpy as np
import cv2

from deepface import DeepFace
from deepface.detectors import FaceDetector
from deepface.commons import functions, distance
from global_logger import configure_logger

class FacesConfigManager:
    def __init__(self, params_filepath: Path) -> None:
        defaults = self.load_defaults()
        self.params = defaults
        with params_filepath.open() as f:
            params = json.load(f)
        self.params.update(params)
        self.config()
        self.validate()
        return
    # end __init__()

    def load_defaults(self) -> dict:
        defaults_json_string = """
        {
            "root_images_dir": 'pictures',
            "identification_model_name": "DeepFace",
            "detector_model_name": "mtcnn",
            "normalization": "base",
            "grayscale": false,
            "align": true,
            "silent": false,
            "distance_metric": "cosine",
            "distance_threshold": null,
            "use_program_dir_for_logs": false,
            "force_early_model_build": false,
            "metadata_dirname": ".faces",
            "metadata_extension": ".json",
            "image_file_types": [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"],
            "debug": false,
            "debug_max_files_to_process": 1000000000,
            "debug_max_faces_to_process": 1000000000,
            "debug_use_deepface_represent": false
        } """
        self.defaults: dict = json.loads(defaults_json_string)
        return self.defaults
    # end load_defaults()

    def config(self):
        self.root_images_dir = self.params["root_images_dir"]
        self.identification_model_name = self.params["identification_model_name"]
        self.detector_model_name = self.params["detector_model_name"]
        self.normalization = self.params["normalization"]
        self.grayscale = self.params["grayscale"]
        self.align = self.params["align"]
        self.silent = self.params["silent"]
        self.distance_metric = self.params["distance_metric"]
        self.distance_threshold = self.params['distance_threshold']
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

        self.image_file_types_glob: str = '|'.join(f'*{ext}' for ext in self.image_file_types)

        # from DeepFace
        self.identification_model_names: list[str] = [
            'VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace', 'DeepID',
            'Dlib', 'ArcFace', 'SFace']

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
        
        # from DeepFace
        self.distance_metrics: list[str] = ['cosine', 'euclidean', 'euclidean_l2']
                        
        # from DeepFace functions
        self.normalizations: list[str] = ['base', 'raw', 'Facenet', 'Facenet2018', 'VGGFace', 'VGGFace2', 'ArcFace']
        
        self.target_size: tuple[int,int] = functions.find_target_size(model_name=self.identification_model_name)

        if self.distance_threshold is None:
            self.distance_threshold = distance.findThreshold(self.identification_model_name,
                                                             self.distance_metric)

        self.enforce_detection: bool = False
        self.face_detector_model = None
        self.identification_model = None
        return
    # end config()
    
    def validate(self) -> None:
        assert self.root_images_dir.exists(), \
            f'Pictures directory {self.root_images_dir.as_posix()} does not exist.'

        norms_string: str = ", ".join(string for string in self.normalizations)
        assert self.normalization in self.normalizations, \
            f'Invalid face identification model: {self.normalizations}. Valid values are {norms_string}'
        
        detect_string: str = ", ".join(string for string in self.face_detectors)
        assert self.detector_model_name in self.face_detectors, \
            f'Invalid face detection model: {self.detector_model_name}. Valid values are {detect_string}'
        
        identify_string: str = ", ".join(string for string in self.identification_model_names)
        assert self.identification_model_name in self.identification_model_names, \
            f'Invalid face identification model: {self.identification_model_name}. Valid values are {identify_string}'

        metrics_string: str = ", ".join(string for string in self.distance_metrics)
        assert self.distance_metric in self.distance_metrics, \
            f'Invalid distance metric: {self.distance_metric}. Valid metrics are: {metrics_string}'

        assert isinstance(self.distance_threshold, float), \
            f'Distance threshold must be a float'
        return
    # end validate()
# end class FacesConfigManager

debug: bool = True

class FileOps:
    def __init__(self,
                 config: FacesConfigManager,
                 logger: logging.Logger):
        global log
        
        self.config = config
        self.log = logger
        log = self.log
    # end __init__()

    def get_logger(self):
        return self.log

    def get_images_dir(self) -> Path:
        return self.config.root_images_dir

    def get_image(self, filepath: Path) -> np.ndarray:
        image = cv2.imread(filepath.as_posix())
        return image
    # end get_image()

    def get_image_files_in_dir(self, dir_path: Path) -> list[Path]:
        return [file for file in dir_path.iterdir() if file.is_file() and file.suffix in self.config.image_file_types]
    # end get_image_files_in_dir

    def make_metadata_dir(self, dir_path: Path) -> Path:
        metadata_path: Path = dir_path / self.config.metadata_dirname
        metadata_path.mkdir(parents=False, exist_ok=True)
        return metadata_path
    # end make_metadata_dir()

    def get_metadata_dirpath(self, image_path: Path) -> Path:
        metadata_dirpath: Path = image_path.parent / self.config.metadata_dirname
        assert metadata_dirpath.exists(), f'Metadata directory does not exist: {metadata_dirpath.as_posix()}'
        return metadata_dirpath
    # end get_metadat_dirpath()
    
    def get_metadata_filename(self, image_filepath: Path) -> str:
        return f'{image_filepath.name}{self.config.metadata_extension}'

    def get_metadata_filepath(self, image_filepath: Path) -> Path:
        metadata_dirpath = self.get_metadata_dirpath(image_filepath)
        face_filepath = metadata_dirpath / self.get_metadata_filename(image_filepath)
        return face_filepath
    # end generate_metadata_filepath_name()

    def get_imagepath_from_metadata(self, metadata_filepath: Path) -> Path:
        imagepath: Path = metadata_filepath.parent.parent / Path(metadata_filepath.name).stem
        return imagepath
    # end get_imagepath_from_metadata()

    def save_faces(self, metadata_filepath: Path, faces: list[dict]) -> None:
        json_string: str = json.dumps(faces, indent=4)

        with metadata_filepath.open('w') as md_fp:
            md_fp.write(json_string)
    # end save_faces()

    def get_saved_faces(self, metadata_filepath: Path) -> list[dict] | None:
        if not metadata_filepath.exists():
            return None
        with metadata_filepath.open("r") as md_fp:
            faces = json.load(md_fp)
        return faces
    # end get_saved_faces()

    def is_hidden(self, path: Path) -> bool:
        return path.name.startswith('.')
    # end is_hidden()
# end class FileOps

class FaceModels:
    def __init__(self, config: FacesConfigManager) -> None:
        self.config = config
        self.detector_model_name: str = config.detector_model_name
        self.identification_model_name: str = config.identification_model_name

        if config.force_early_model_build:
            self.face_detector_model = self.get_face_detector_model()
            self.identification_model = self.get_identification_model()
        return
    # end __init__()

    def add_embedding(self, face: list):
        global log
        normalized_face_image, area, confidence = face
        start_time = time.time()
        embedding = self.get_representation(image = normalized_face_image)
        end_time = time.time()
        delta_time = end_time - start_time
        log.info(f'Face representation (embedding) generated in {delta_time} seconds.')
        face_with_embedding: dict = {'name': None, 'area': area, 'confidence': confidence, 'embedding': embedding}
        # face_with_embedding.update(area)
        return face_with_embedding

    def generate_embeddings(self, faces_found: list):
        global log
        faces: list[dict] = []
        face_count = 0
        embeddings_start_time = time.time()
        for face_found in faces_found:
            log.info(f'Generating embedding for face: {face_count}')
            face = self.add_embedding(face_found)
            faces.append(face)
            face_count += 1
        # end for
        end_time = time.time()
        delta_time = end_time - embeddings_start_time
        log.info(f'Face representations (embeddings) for {face_count} face(s) generated in {delta_time} seconds.\n')
        return faces
    # end generate_embeddings()

    def get_face_detector_model(self): # Lazy model build
        global log
        if self.face_detector_model is None:
            log.info(f'Face detection model build starting: {self.detector_model_name}...')
            start_time = time.time()
            self.face_detector_model = FaceDetector.build_model(self.detector_model_name)
            end_time = time.time()
            log.info(f'Face detection model built in {end_time - start_time} seconds.\n')
        return self.face_detector_model
    # end get_face_detector_model()

    def get_representation(self,
                           image: np.ndarray):
        if self.config.normalization is None:
            norm_image = image
        else:
            norm_image = functions.normalize_input(img=image, normalization=self.config.normalization)

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

    def get_identification_model(self): # Lazy model build
        global log
        if self.identification_model is None:
            log.info(f'Identification model build starting: {self.identification_model_name}...')
            start_time = time.time()
            self.identification_model = DeepFace.build_model(self.identification_model_name)
            end_time = time.time()
            log.info(f'Identification model built {end_time - start_time} seconds.\n')
        return self.identification_model
    # end get_identification_model
# end class FaceModels

class FaceDetection:
    def __init__(self, config: FacesConfigManager, face_models: FaceModels) -> None:
        self.debug_use_deepface_represent = False
        self.must_generate_embeddings = not self.debug_use_deepface_represent
        self.config: FacesConfigManager = config
        self.models: FaceModels = face_models
        return
    #end __init__()

    def __get_faces(self, filepath: Path):
        global log
        log.info(f'Finding faces from image: {str(filepath)}\n')
        start_time = time.time()
        
        faces_found = functions.extract_faces(
            img=filepath.as_posix(),
            target_size=self.config.target_size,
            detector_backend=self.config.detector_model_name,
            enforce_detection=self.config.enforce_detection,
            align=self.config.align,
            grayscale=self.config.grayscale)
            
        end_time = time.time()
        delta_time = end_time - start_time
        face_count = len(faces_found)
        log.info(f'Found {len(faces_found)} face(s) in {delta_time} seconds from image {filepath.as_posix()}')

        return faces_found
    # end __get_faces

    def get_from_file(self, filepath: Path) -> list[dict]:
        faces_found = self.__get_faces(filepath)
        faces = []
        if len(faces_found) > 0:
            faces = self.models.generate_embeddings(faces_found)
        return faces    
    # end get_from_file

# end class FaceDetection

class FaceIdentification:
    def __init__(self, config: FacesConfigManager, face_models: FaceModels) -> None:
        self.config: FacesConfigManager = config
        self.models: FaceModels = face_models
        return

    def compare(self, face1: dict, face2: dict) -> bool:
        embedding1 = face1['embedding']
        embedding2 = face2['embedding']
        distance_metric = self.config.distance_metric
        if distance_metric == "cosine":
            dist = distance.findCosineDistance(embedding1, embedding2)
        elif distance_metric == "euclidean":
            dist = distance.findEuclideanDistance(embedding1, embedding2)
        elif distance_metric == "euclidean_l2":
            dist = distance.findEuclideanDistance(
                distance.l2_normalize(embedding1), distance.l2_normalize(embedding2)
            )
        else:
            raise ValueError("Invalid distance_metric passed - ", distance_metric)
        
        return dist >= self.config.distance_threshold
    # end compare()

# end class FaceIdentification

class FaceFunctions:
    def __init__(self, config: FacesConfigManager):
        self.config = config
        self.face_models = FaceModels(config)
        self.face_detection = FaceDetection(config, self.face_models)
        self.face_identification = FaceIdentification(config, self.face_models)

    def get_from_area(self, image: np.ndarray, area: dict[str, int]) -> np.ndarray:
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        return image[y:y+h, x:x+w]
    # end get_from_area()

    def __mark_face(self, 
                    image: np.ndarray,
                    face: dict,
                    box_color: tuple[int,int,int] = (0, 255, 0),
                    display_size: int = 1024,
                    show_window: bool = True) -> None:
        area = face['area']
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        cv2.rectangle(image, (x, y), (x+w, y+h), box_color, 2)
        return
    # end __mark_face()

    def __resize_image(self, image, display_size) -> np.ndarray:
        h, w, _ = image.shape
        image_ratio = float(h) / float(w)
        desired_size = (display_size, int(image_ratio * display_size))
        resized_image = cv2.resize(image, (desired_size))
        return resized_image
    # end __resize_image

    def view_faces(self, image: np.ndarray, faces: list[dict], display_size=1024, show_window=True):
        resized_image = self.__resize_image(image, display_size)
        output = resized_image.copy()

        if show_window:
            cv2.namedWindow('Image', cv2.WINDOW_AUTOSIZE)
        for face in faces:
            self.__mark_face(output, face)
            cv2.imshow('Image', output)
            cv2.waitKey(0)
        if show_window:
            cv2.destroyWindow('Image')
        return

    def detect(self, filepath: Path):
        faces = self.face_detection.get_from_file(filepath)
        return faces

    def identify(self, filepath: Path) -> str:
        metadata_dir = self.config.metadata_dirname
        metadata_extension = self.config.metadata_extension
        name: str = str("")
        return name
# end class FaceFunctions
