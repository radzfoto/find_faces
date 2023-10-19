from typing import Any, Pattern, Iterator
import unittest
from pathlib import Path
from attr import dataclass
from deepdiff import DeepDiff
from send2trash import send2trash
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
    #        is_iterator allows iteration on only all dirs in dir tree, only all files in dir tree, or both.
    #       
    #        match_dirs and match_files are each a list of single glob expressions such as ['*.jpg', '*.jpeg'].
    #        Files or directories that match any of glob patterns in the list will be matched

    def __init__(self,
                 root_dir: Path,
                 match_dirs: list[str] = ['*'],
                 match_files: list[str] = ['*'],
                 ignore_hidden: dict[str, bool] = {'dirs': True, 'files': True},
                 ignore_list: dict[str, list[str]] = {'dirs': ['.DS_Store', '.Trash'], 'files': ['.DS_Store']},
                 is_iterator: dict[str, bool] = {'dirs': True, 'files': True}
                 ) -> None:

        # ENABLE DEBUG MODE
        #self.debug: bool = True

        self._saved_root_dir: Path = root_dir
        self._saved_match_dirs: list[str] = match_dirs
        self._saved_match_files: list[str] = match_files
        self._saved_ignore_hidden: dict[str, bool] = ignore_hidden
        self._saved_ignore_list: dict[str, list[str]] = ignore_list
        self._saved_is_iterator: dict[str, bool] = is_iterator

        self._setup()
    # end __init__()

    def _setup(self) -> None:
        self._is_iterator: dict[str,bool] = self._saved_is_iterator
        self._directories: list[Path] = [self._saved_root_dir]
        self._current_dir: Path = Path()
        self._files_in_current_dir: list[Path] = []
        self._files_indicator:bool = False
        self._ignore_dirs: list[str] = self._saved_ignore_list['dirs']
        self._ignore_files: list[str] = self._saved_ignore_list['files']

        self._ignore_hidden_files: bool = self._saved_ignore_hidden['files']
        self._ignore_hidden_dirs: bool =  self._saved_ignore_hidden['dirs']

        match_dir_pattern: Pattern[str] = self._make_pattern(self._saved_match_dirs)
        match_file_pattern: Pattern[str] = self._make_pattern(self._saved_match_files)
        self._match_dirs: Pattern[str] = match_dir_pattern
        self._match_files: Pattern[str] = match_file_pattern

        if self._is_iterator['files'] and not self._is_iterator['dirs']:
            self._get_next_dir() # Initialize file iterator
    # end _setup()

    def _make_pattern(self, glob_pattern_list: list[str]) -> Pattern[str]:
        regex_parts: list[str] = [fnmatch.translate(part) for part in glob_pattern_list]

        regex_pattern: str = '|'.join(regex_parts)

        regex: Pattern[str] = re.compile(regex_pattern, re.IGNORECASE)

        return regex
    # end _make_pattern()

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

            must_append: bool = False
            for path in self._current_dir.iterdir():
                must_append = path.is_file()
                must_append = must_append and (path.name not in self._ignore_files)
                must_append = must_append and (self._match_files.match(string=path.name) is not None)
                must_append = must_append and ((self._ignore_hidden_files and not path.name.startswith('.')) or (not self._ignore_hidden_files))
                if must_append:
                    self._files_in_current_dir.append(path)
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

    def _iterate_files(self) -> Path:
        assert self._is_iterator['files'], f'{self.__class__.__name__} instance has disabled file iteration.'

        if self._current_dir == Path():
            if self._is_iterator['dirs']:
                return self._iterate_dirs()
            else:
                self._get_next_dir()

        next_file: Path = self._get_next_file()

        if next_file != Path():
            return next_file
        else:
            if self._is_iterator['dirs']:
                return self._iterate_dirs()
            else:
                next_dir: Path = self._get_next_dir()
                
            while next_dir != Path():
                next_file = self._get_next_file()
                if next_file != Path():
                    return next_file
                next_dir = self._get_next_dir()
        raise StopIteration
    # end _iterate_files(self)

    def __next__(self) -> Path:
        if self._is_iterator['dirs'] and not self._is_iterator['files']:
            return self._iterate_dirs()
        elif not self._is_iterator['dirs'] and self._is_iterator['files']:
            return self._iterate_files()
        elif self._is_iterator['dirs'] and self._is_iterator['files']:
            return self._iterate_files()
        else:
            raise StopIteration
    # end __next__()

    def next_dir(self) -> Path:
        return self._get_next_dir()
    # end next_dir()

    def next_file(self) -> Path:
        if self._is_iterator['files']:
            return self._get_next_file()
        else:
            return self._iterate_files()
    # end next_file()

    def restart(self) -> None:
        self._setup()
        return
    # end restart()
# end class Traverser()

class TestTraverser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path('./test_dir')
        cls.create_test_dir_tree(cls.root_dir)
    # end setUpClass()

    @classmethod
    def tearDownClass(cls):
        # cleanup to delete the test directory
        for child in reversed(list(cls.root_dir.rglob('*'))):
            if child.is_file():
                child.unlink()
            else:
                child.rmdir()
        cls.root_dir.rmdir()
    # end tearDownClass()

    @classmethod
    def create_test_dir_tree(cls, root_dir: Path) -> dict[Path, set[str]]:

        dir_tree: dict[Path, set[str]] = {}
        dir_tree[root_dir] = set()
        dir_tree[Path(root_dir / 'dir1')] = set(['file1_1', 'file1_2', 'file_1_3', '.file1_4', '.file1_5'])
        dir_tree[Path(root_dir / 'dir2')] = set()
        dir_tree[Path(root_dir / 'dir2' / 'dir2_1')] = set(['file2_1'])
        dir_tree[Path(root_dir / 'dir2' / 'dir2_2')] = set()
        dir_tree[Path(root_dir / 'dir2' / '.dir2_3')] = set()
        dir_tree[Path(root_dir / '.dir3')] = set()
        dir_tree[Path(root_dir / '.dir4')] = set(['.file4_1']) 

        root_dir.mkdir(exist_ok=True)
        for dir in dir_tree:
            dir_path: Path = dir
            dir_path.mkdir(exist_ok=True)
            assert dir_path.exists(), f'Error: unable to create directory: {dir_path.as_posix()}'
            for filename in dir_tree[dir]:
                filepath = dir_path / filename
                with filepath.open('w') as f:
                    f.write('Some text')
                assert filepath.exists(), f'Error: unable to create file: {filepath.as_posix()}'

        return dir_tree
    # end create_test_dir_tree()

    def test_traverse_only_dirs(self) -> None:
        traverser = Traverser(self.root_dir, is_iterator={'dirs': True, 'files': False}, ignore_hidden={'dirs': False, 'files': False})
        actual_dirs = set()
        for dir in traverser:
            actual_dirs.add(dir)

        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        self.assertEqual(expected_dirs, actual_dirs)
        return
    # end test_traverse_only_dirs()

    def test_traverse_only_dirs_ignore_hidden(self) -> None:
        traverser = Traverser(self.root_dir, is_iterator={'dirs': True, 'files': False})
        actual_dirs = set()
        for dir in traverser:
            actual_dirs.add(dir)

        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2'])
        self.assertEqual(expected_dirs, actual_dirs)
        return
    # end test_traverse_only_dirs_ignore_hidden()

    def test_traverse_only_files(self) -> None:
        traverser = Traverser(self.root_dir, is_iterator={'dirs': False, 'files': True}, ignore_hidden={'dirs': False, 'files': False})
        actual_files = set()
        for file in traverser:
            actual_files.add(file)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        self.assertEqual(expected_files, actual_files)
        return
    # end test_traverse_only_files()

    def test_traverse_only_files_ignore_hidden(self) -> None:
        traverser = Traverser(self.root_dir, is_iterator={'dirs': False, 'files': True})
        actual_files = set()
        for file in traverser:
            actual_files.add(file)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1'])
        self.assertEqual(expected_files, actual_files)
        return
    # end test_traverse_only_files_ignore_hidden()

    def test_traverse_all(self) -> None:
        traverser = Traverser(self.root_dir, ignore_hidden={'dirs': False, 'files': False})
        actual_files = set()
        for file in traverser:
            actual_files.add(file)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        expected = expected_dirs | expected_files
        self.assertEqual(expected, actual_files)
        return
    # end test_traverse_only_files()

    def test_manual_traverse_all(self) -> None:
        traverser = Traverser(self.root_dir, ignore_hidden={'dirs': False, 'files': False})
        actual_files = set()
        dir: Path = traverser.next_dir()
        if dir != Path():
            actual_files.add(dir)
        while dir != Path():
            file: Path = traverser.next_file()
            if file != Path():
                actual_files.add(file)
            while file != Path():
                file = traverser.next_file()
                if file != Path():
                    actual_files.add(file)
            dir: Path = traverser.next_dir()
            if dir != Path():
                actual_files.add(dir)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        expected = expected_dirs | expected_files
        self.assertEqual(expected, actual_files)
        return
    # end test_manual_traverse_all()
    
    def test_traverse_all_using_next(self) -> None:
        traverser = Traverser(self.root_dir, ignore_hidden={'dirs': False, 'files': False})
        actual_files = set()
        keep_going = True
        file = Path()
        try:
            file = next(traverser)
        except StopIteration:
            keep_going = False

        while keep_going and (file != Path()):
            actual_files.add(file)
            try:
                file = next(traverser)
            except StopIteration:
                keep_going = False

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        expected = expected_dirs | expected_files
        self.assertEqual(expected, actual_files)
        return
    # end test_traverse_all_using_next()

# end class TestTraverser

if __name__ == '__main__':
    unittest.main()
