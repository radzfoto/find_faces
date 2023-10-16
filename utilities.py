# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces
import sys
from pathlib import Path
import cv2
import json
import numpy as np
import networkx as nx
import pickle
from global_logger import GlobalLogger

debug = False
visualization_on = True
show_windows_on_visualization = False

image_file_types = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']

class JSONNumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JSONNumpyEncoder, self).default(obj)
# end JSONNumpyEncoder

logger_config = GlobalLogger(None, None)  # Use default settings or already configured settings
log = logger_config.global_logger

class TraverseTree:

    def __init__(self, root_dir: Path, match=None):
        pass
    # end __init__()

    def get_dirs(self, dir_path: Path, pattern=None) -> list[Path]:
        # files = [f for f in path.iterdir() if f.is_file()]
        dirs = [d for d in dir_path.iterdir() if d.is_file()]
    # end get_dirs

    def get_files(self, dir_path: Path, pattern=None) -> list[Path]:
        # files = [f for f in path.iterdir() if f.is_file()]
        files = [f for f in dir_path.iterdir() if f.is_file()]
    # end get_dirs

# end class

def split_list(a_list: list, chunk_size: int):
    start_index = 0
    list_len = len(a_list)
    chunk_list = []
    for i in range(start_index, list_len, chunk_size):
        n = i + chunk_size
        if n > list_len:
            n = list_len
        chunk = a_list[i: i + n]
        chunk_list.append(chunk)

    return chunk_list
# end split_list

def get_dir_list(p: Path) -> list[Path]:
    error_msg = 'Directory does not exist: ' + p.as_posix()
    if not (p.exists() and p.is_dir()):
        log.error(error_msg)
    assert p.exists() and p.is_dir(), error_msg
    dirs: list = [p]
    for item in p.iterdir():
        if item.is_dir():
            name = item.name
            # Skip hidden directories
            if name[0] != '.':
                dirs.extend(get_dir_list(item))
    return dirs
# end get_dir_list

# def get_dirs_df(p: Path, column_name: str = None) -> pd.DataFrame:
#     dir_list = get_dir_list(p)
#     df: pd.DataFrame = pd.DataFrame(dir_list)
#     if column_name is not None:
#         df.columns = [column_name]
# # end get_dirs_df

def get_files_in_dir(a_dir: Path) -> list[Path]:
    error_msg = 'Directory does not exist: ' + a_dir.as_posix()
    assert a_dir.exists(), error_msg
    images_file_list = [f for f in a_dir.iterdir() if (f.is_file() and (f.suffix in image_file_types))]
    return images_file_list
# end get_file_list

def get_filenames_in_paths(paths: list[Path], filenames: list[str]):
    filenames_in_paths: list[str] = \
         [path.name for path in paths if path.name in filenames]
    return filenames_in_paths
# end get_filenames_in_paths()

def get_filenames_not_in_paths(paths: list[Path], filenames: list[str]):
    filenames_not_in_paths: list[str] = \
         [path.name for path in paths if path.name not in filenames]
    return filenames_not_in_paths
# end get_filenames_not_in_paths()

def add_edges(graph, node: Path, parent=None):
    if parent is not None:
        graph.add_edge(parent, node)
    dir_list = get_dir_list(node)
    for child in dir_list:
        child_path = node / child
        if child_path.is_dir():
            add_edges(graph, child_path, node)
        else:
            graph.add_edge(node, child_path)
# end add_edges

def get_dir_tree(a_dir: Path) -> nx.DiGraph:
    tree_graph: nx.DiGraph = nx.DiGraph()
    add_edges(tree_graph, a_dir)
    return tree_graph
# end get_dir_tree

# Breadth first traversal of tree
def bfs_traversal(graph, start_node):
    return list(nx.bfs_tree(graph, start_node))
# end bfs_traversal

def box_is_inside(image_width: int, image_height: int, bx: int, by: int, bw: int, bh: int) -> bool:
    if debug:
        print('iwidth: ' + str(image_width) + ' iheight: ' + str(image_height) + ' X1: ' + str(bx) + ' Y1: ' + str(by) + ' X2: ' + str(bx+bw) + ' Y2: ' + str(by+bh))
        pass
    is_inside = True
    is_inside = is_inside and (bx >= 0)
    is_inside = is_inside and (by >= 0)
    is_inside = is_inside and ((bx + bw) <= image_width)
    is_inside = is_inside and ((by + bh) <= image_height)
    return is_inside
# end box_is_inside

def make_box_corrections(image_width: int, image_height: int, bx: int, by: int, bw: int, bh: int) -> tuple[int, int, int, int]:
    x, y, w, h = bx, by, bw, bh

    is_outside: bool = False

    if bx < 0:
        is_outside = True
        x = 0
        w = w + bx
    
    if by < 0:
        is_outside = True
        y = 0
        h = h + bh

    x2, y2 = x + w, y + h

    if (x2 > image_width):
        is_outside = True
        w = w - (x2 - image_width)

    if (y2 > image_height):
        is_outside = True
        h = h - (y2 - image_height)

    if is_outside:
        print('Face coordinates outside of image: iwidth: ' + str(image_width) + ' iheight: ' + str(image_height) + ' X: ' + str(bx) + ' Y: ' + str(by) + ' W: ' + str(bw) + ' H: ' + str(bh))
        print('Corrected to:                                             ' + ' X: ' + str(x) + ' Y: ' + str(y) + ' W: ' + str(w) + ' H: ' + str(h))
        # x2, y2 = x + w, y + h

    return (x, y, w, h)
# end make_box_corrections

def write_image_file(image: np.ndarray,
                     image_filename: Path,
                     exception_on_write_fail = False):
    cv2.imwrite(image_filename.as_posix(), image)
    if not image_filename.exists():
        if exception_on_write_fail:
            raise FileExistsError('Unable to create file: ' + str(image_filename))
        else:
            print('WARNING: unable to create file: ' + str(image_filename), file=sys.stderr)
    return
# end write_image_file

def read_image_file(image_filename: Path,
                    exception_on_read_fail = False) -> np.ndarray:
    image = cv2.imread(image_filename.as_posix())
    if image is None:
        if exception_on_read_fail:
            raise FileExistsError('Unable to read file: ' + str(image_filename))
        else:
            print('WARNING: unable to read file: ' + str(image_filename), file=sys.stderr)
    
    return image
# end read_image_file

def read_pickle_file(pickle_filename: Path,
                     read_mode: str = 'rb',
                     exception_on_read_fail = False):
    try:
        with pickle_filename.open(read_mode) as pkl_file:
            pkl_data = pickle.load(pkl_file)
            return pkl_data
    except FileNotFoundError as e:
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: Could not find file: ' + str(pickle_filename.as_posix()))
            return None
    except PermissionError:
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: Cannot access file: ' + str(pickle_filename.as_posix()))
            return None
    except EOFError as e:
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: Pickle file is truncated or corrupted')
            return None
    except (KeyError, IndexError, AttributeError) as e:
        print('Invalid pickle data format')
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: Invalid pickle data format')
            return None
    except ImportError as e:
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: importing module in pickle')
            return None
    except Exception as e:
        if exception_on_read_fail:
            raise e
        else:
            print('Warning: Unknown error loading pickle data')
            return None
# end read_pickle_file

def visualize(image: np.ndarray,
              bounding_boxes: list[int,int,int,int] = [],
              box_color: tuple[int,int,int] = (0, 255, 0),
              display_size: int = 1024,
              show_window: bool = True) -> np.ndarray:
    if not isinstance(image, np.ndarray):
        # Results can be None or empty list [] which apparently cannot be compared to results if results is type np.ndarray
        output = None
    else:
        output = image.copy()

        for box in bounding_boxes:
            x, y, w, h = box[0], box[1], box[2], box[3]
            cv2.rectangle(output, (x, y), (x+w, y+h), box_color, 2)

        h, w, _ = image.shape
        image_ratio = float(h) / float(w)
        desired_size = (display_size, int(image_ratio * display_size))
        output = cv2.resize(output, (desired_size))

        if show_window:
            cv2.namedWindow('Image', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Image', output)
            cv2.waitKey(0)
            cv2.destroyWindow('Image')

    return output
# end visualize