import json
from pathlib import Path
import numpy as np
import logging

from global_logger import configure_logger
from traverser import Traverser, FileTraverser, DirTraverser
from faces import FacesConfigManager, FileOps, FaceFunctions
from remove_metadata import remove_metadata

debug: bool
log: logging.Logger

def detect_faces_loop(config: FacesConfigManager, face_functions: FaceFunctions, file_ops: FileOps):
    dir_traverser = DirTraverser(config.root_images_dir,
                              ignore_hidden=True)
    
    for dirpath in dir_traverser:
        for file in file_ops.get_image_files(dirpath):
            metadata_filepath = file_ops.generate_metadata_filepath(file)
            if not metadata_filepath.exists():  # if the metadata already exists for that image, then skip it
                faces = face_functions.detect(file)
                file_ops.save_faces(metadata_filepath, faces)
    return
# end detect_faces_loop()

def view_faces_loop(file_ops: FileOps, face_functions: FaceFunctions) -> None:
    global log

    dir_traverser = DirTraverser(root_dir=file_ops.get_images_dir(), ignore_hidden=False)

    for dirpath in dir_traverser:
        if dirpath.name == file_ops.get_metadata_dirname(): 
            for file in file_ops.get_metadata_files(dirpath):
                image_path = file_ops.get_imagepath_from_metadata(file)
                if image_path.exists():
                    faces = file_ops.get_saved_faces(file)
                    if faces is None:
                        log.info(f'No faces available for image file: {file.as_posix()}')
                    else:
                        image = file_ops.get_image(image_path)
                        if image is None:
                            log.info(f'Unable to open image file: {file.as_posix()}')
                        else:
                            face_functions.view_faces(image, faces)
                else:
                    log.info(f'File does not exist: {image_path.as_posix()}')
    return
# end view_faces_loop()

def main() -> None:
    global log
    global debug

    debug = True
    must_remove_metadata: bool = False
    must_view_faces: bool = True

    log_name: str = Path(Path(__file__).name).stem
    log_path = Path(log_name + '.log')
    log = configure_logger(log_name, log_file=log_path, debug=debug)
    
    operating_parameters_filename: str = 'faces_parameters.json'
    operating_parameters_path = Path(__file__).parent / operating_parameters_filename

    faces_config = FacesConfigManager(operating_parameters_path)
    file_ops = FileOps(faces_config, logger=log)
    face_functions: FaceFunctions = FaceFunctions(faces_config)

    if must_remove_metadata:  # For debugging or when needing to regenerate all face metadata
        remove_metadata(file_ops.get_images_dir())

    # Skips images that already have face metadata files
    detect_faces_loop(faces_config, face_functions, file_ops)

    if must_view_faces:
        view_faces_loop(file_ops, face_functions)
    return
# end main

if __name__ == '__main__':
    main()