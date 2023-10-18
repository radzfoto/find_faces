from typing import Any, Pattern, Iterator
from pathlib import Path
import re
import fnmatch
from global_logger import GlobalLogger

class Traverser:
    # USAGE: instantiate a Traverser object such as traverer = Traverser(/dirtree/to/traverse)
    #        then call traverse.next_dir() and traverse.next_file() or use the traverser object as an
    #        iterator.
    #
    #        When used as an iterator object, traverser will yield either all the directories in
    #        the tree or all the files in the tree, depending the is_dir_iterator (see below).
    #
    #        traverse.next_dir() will yield the tree directories one at a time for the entire tree
    #        traverse.next_file() will yield all the files in the current directory one at a time
    #        If traverser.next_dir() is called before traverser.next_file() has yielded the last
    #        file in the current directory, the next call to traverser.next_file() will yield the
    #        first file in the next directory. Both next_dir and next_file return None when there
    #        are no more dirs or files to yield.
    #
    #        ignore_hidden overrides ignore_hidden_files and ignore_hidden_dirs unless ignore_hidden
    #        is False, in which case whatever the others are will be used.
    #
    #        parameter is_dir_iterator is used to create a directory tree iterator if true. If false,
    #        then the instance becomes a file iterator of the directory tree. Note that the iterator
    #        can be ignored or overriden by calling next_dir or next_file directly, although this should
    #        be used cautiously. For safety, either use the iterator function or call next_dir
    #        and next_file directly, but not both.
    #
    #       If is_dir_iterator is True, then gets_files_in_curr_dir is also set to True. This allows
    #       the next_file method to be used in conjunction with the directory iterator.

    def __init__(self,
                 root_dir: Path,
                 match_dirs: str = '*',
                 match_files: str = '*',
                 ignore_hidden: dict[str, bool] = {'dirs': True, 'files': True},
                 ignore_list: dict[str, list[str]] = {'dirs': ['.DS_Store', '.Trash'], 'files': ['.DS_Store']},
                 is_dir_iterator: bool = False,  # True makes this a file iterator, False makes this a directory iterator
                 gets_files_in_curr_dir: bool = False, # next_file and file iterator only iterate over the current directory, use next_dir to go to next_dir explicitly
                 ) -> None:

        # ENABLE DEBUG MODE
        #self.debug: bool = True

        self._is_dir_iterator: bool = is_dir_iterator
        self._gets_files_in_curr_dir: bool = gets_files_in_curr_dir
        self._directories: list[Path] = [root_dir]
        self._current_dir: Path = Path()
        self._files_in_current_dir: list[Path] = []
        self._files_indicator:bool = False
        self._ignore_dirs: list[str] = ignore_list['dirs']
        self._ignore_files: list[str] = ignore_list['files']

        if self._is_dir_iterator:
            self._gets_files_in_curr_dir: bool = True

        self._ignore_hidden_files: bool = ignore_hidden['files']
        self._ignore_hidden_dirs: bool =  ignore_hidden['dirs']
        self._match_dirs: Pattern[str] = re.compile(pattern=fnmatch.translate(pat=match_dirs))
        self._match_files: Pattern[str] = re.compile(pattern=fnmatch.translate(pat=match_files))
    # end __init__()

    def _get_next_dir(self) -> Path:
        while self._directories:
            self._current_dir = self._directories.pop(0)
            dir_name : str = self._current_dir.name
            if dir_name in self._ignore_dirs or \
                           (self._ignore_hidden_dirs and dir_name.startswith('.')):
                continue
            if self._match_dirs.match(string=dir_name):
                for path in self._current_dir.iterdir():
                    if path.is_dir() and (path.name not in self._ignore_dirs) and \
                       ((self._ignore_hidden_dirs and not (path.name).startswith('.')) or (not self._ignore_hidden_dirs)):
                        self._directories.append(path)
                self._files_in_current_dir = []
                self._files_indicator = False
                return self._current_dir
        return Path()
    # end _get_next_dir()

    def _get_next_file(self)-> Path:
        if not self._files_indicator:
            if self._current_dir == Path():  # This happens if next_file is called before next_dir()
                self._get_next_dir()
            self._files_in_current_dir = [
                path for path in self._current_dir.iterdir() if \
                    path.is_file() and (path.name not in self._ignore_files) and self._match_files.match(string=path.name) and
                    ((self._ignore_hidden_files and not path.name.startswith('.')) or (not self._ignore_hidden_files))
                    ]
            self._files_indicator = True

        if len(self._files_in_current_dir) > 0:
            return self._files_in_current_dir.pop(0)
        else: # No files found in current dir
            return Path()

    # end _get_next_file()

    def __iter__(self) -> Iterator[Path]:
        return self
    # end __iter__()

    def _iterate_dirs(self) -> Path:
        next_dir: Path = self._get_next_dir()
        if next_dir == Path():
            raise StopIteration
        return next_dir
    # end _iterate_dirs()

    def _iterate_files(self, no_stop_iteration=False) -> Path:
        next_file: Path = self._get_next_file()
        if self._gets_files_in_curr_dir:
            if next_file == Path():
                if no_stop_iteration:
                    return Path()
                else:
                    raise StopIteration
        else:
            if next_file != Path():
                return next_file

            next_dir: Path = self._get_next_dir()
            while next_dir != Path():
                next_file = self._get_next_file()
                if next_file != Path():
                    return next_file
                next_dir = self._get_next_dir()

            if no_stop_iteration:
                return Path()
            else:
                raise StopIteration
        return Path()
    # end _iterate_files(self)

    def __next__(self) -> Path:
        if self._is_dir_iterator:
            return self._iterate_dirs()
        else:
            return self._iterate_files(no_stop_iteration=False)
    # end __next__()

    def next_dir(self) -> Path:
        return self._get_next_dir()
    # end next_dir()

    def next_file(self) -> Path:
        if self._gets_files_in_curr_dir:
            return self._get_next_file()
        else:
            return self._iterate_files(no_stop_iteration=True)
    # end next_file()
# end class TreeTraverser()

# class ImageNavigator:
#     def __init__(self, traverser: Traverser, on_name: Callable) -> None:
#         logging_info = GlobalLogger()
#         log = logging_info.global_logger

#         self.traverser: Traverser = traverser
#         self.on_name = on_name
#         self.current_image_data = Path()
#     # end __init__()

#     def display_image(self) -> None:
#         for i in range(1000):
#             self.current_image_data: Path = next(self.traverser)
#     # end display_image()
# # end class ImageNavigator

def test() -> None:
    def run_test(traverser: Traverser) -> int:
        logging_info = GlobalLogger()
        log = logging_info.global_logger
        counter = 0
        for file in traverser:
            if file.is_dir():
                log.info(f'Dir: {file.as_posix()}')
            elif file.is_file():
                log.info(f'File: {file.as_posix()}')
            else:
                log.info(f'Object {file.as_posix()} type unknown.')
            counter += 1
            if counter > (max_dir_count_allowed*max_file_count_allowed):
                break
        return counter
    # end run_test()

    logger_config = GlobalLogger(log_dir=Path(__file__).parent,
                                        log_filename='traverser.log',
                                        log_level=GlobalLogger.DEBUG,
                                        log_messages_to_console=True)
    log = logger_config.global_logger
    log.info('****--------- Starting Traverser Tests -------------***')

    # Create test dir tree
    root_dir: Path = Path(__file__).parent / 'test_traverser'
    root_dir: Path = Path().home()
    root_dir.mkdir(exist_ok=True)
    dir1: Path = root_dir / Path('dir1')
    dir1.mkdir(exist_ok=True)
    dir2: Path = root_dir / Path('dir2')
    dir2.mkdir(exist_ok=True)
    dir2_1: Path = dir2 / Path('dir2_1')
    dir2_1.mkdir(exist_ok=True)
    dir3: Path = root_dir / Path('.dir3')
    dir3.mkdir(exist_ok=True)
    dir4: Path = root_dir / Path('.dir4')
    dir4.mkdir(exist_ok=True)

    with (dir1 / 'file1_1').open('w') as f:
        f.write('Some text')

    with (dir1 / 'file1_2').open('w') as f:
        f.write('Some text')

    with (dir1 / 'file1_3').open('w') as f:
        f.write('Some text')

    with (dir1 / '.file1_4').open('w') as f:
        f.write('Some text')

    with (dir2 / 'file2_1').open('w') as f:
        f.write('Some text')

    with (dir4 / '.file4_1').open('w') as f:
        f.write('Some text')

    max_dir_count_allowed: int = 50  # For testing to prevent infinite loops and long tests
    max_file_count_allowed: int = 100  # For testing to prevent infinite loops and long tests

    # Alternative test: root_dir = Path().home() / Path('pics_test/test_small'
    all_dir_traverser = Traverser(root_dir, ignore_hidden={'files': False, 'dirs': False}, is_dir_iterator=True)
    dir_traverser = Traverser(root_dir=root_dir, is_dir_iterator=True)
    all_file_traverser = Traverser(root_dir, ignore_hidden={'files': False, 'dirs': False})
    file_traverser = Traverser(root_dir)
    file_cur_dir_traverser = Traverser(root_dir, ignore_hidden={'files': False, 'dirs': False}, gets_files_in_curr_dir=True)

    log.info('------------- Start all_dir_traverser')
    run_test(all_dir_traverser)
    log.info('------------- End all_dir_traverser')

    log.info('------------- Start dir_traverser')
    run_test(dir_traverser)
    log.info('------------- End dir_traverser')

    log.info('------------- Start all_file_traverser')
    run_test(all_file_traverser)
    log.info('------------- End all_file_traverser')

    log.info('------------- Start file_traverser')
    run_test(file_traverser)
    log.info('------------- End file_traverser')

    log.info('------------- Start file_cur_dir_traverser')
    run_test(file_cur_dir_traverser)
    log.info('------------- End file_cur_dir traverser')

    log.info('****--------- Completed Traverser Tests -------------***')

    return
# end test()

if __name__ == '__main__':
    test()
