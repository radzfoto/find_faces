import json
from pathlib import Path
import numpy as np
import logging

from global_logger import configure_logger
from traverser import Traverser, FileTraverser, DirTraverser
from faces import FacesConfigManager, FileOps, FaceFunctions

debug: bool
log: logging.Logger

def detect_faces_loop(config: FacesConfigManager, face_functions: FaceFunctions):
    file_ops = FileOps(config)

    dir_traverser = DirTraverser(config.root_images_dir,
                              ignore_hidden=True)
    
    for dir in dir_traverser:
        for file in file_ops.get_image_files_in_dir(dir):
            metadata_filepath = file_ops.get_metadata_filepath(file)
            if not metadata_filepath.exists():  # if the metadata already exists for that image, then skip it
                faces = face_functions.detect(file)
                file_ops.save_faces(metadata_filepath, faces)
    return
# end detect_faces_loop()

def view_faces_loop(config: FacesConfigManager, face_functions: FaceFunctions):
    file_ops = FileOps(config)

    dir_traverser = DirTraverser(config.root_images_dir,
                              ignore_hidden=True)

    for dir in dir_traverser:
        for file in file_ops.get_image_files_in_dir(dir):
            metadata_filepath = file_ops.get_metadata_filepath(file)
            faces = file_ops.get_saved_faces(metadata_filepath)
            if faces is None:
                print(f'No faces available for image file: {file.as_posix()}')
            else:
                image = file_ops.get_image(file)
                if image is None:
                    print(f'Unable to open image file: {file.as_posix()}')
                else:
                    face_functions.view_faces(image, faces)
    return
# end view_faces_loop()

def main() -> None:
    global log
    global debug

    debug = True

    log_name: str = Path(Path(__file__).name).stem
    log_path = Path(log_name + '.log')
    log = configure_logger(log_name, log_file=log_path, debug=debug)
    
    operating_parameters_filename: str = 'faces_parameters.json'
    operating_parameters_path = Path(__file__).parent / operating_parameters_filename
    with operating_parameters_path.open('r') as params_file:
        params = json.load(params_file)

    faces_config = FacesConfigManager(params)
    files = FileOps(faces_config, logger=log)
    face_functions: FaceFunctions = FaceFunctions(faces_config)

    if debug:
        

    detect_faces_loop(faces_config, face_functions)

    # view_faces_loop(faces_config, face_functions)
    return
# end main

if __name__ == '__main__':
    main()