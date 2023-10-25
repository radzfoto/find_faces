from pathlib import Path
import unittest
from traverser import DirTraverser, FileTraverser, Traverser
import logging
from global_logger import GlobalLogger

class TestTraverser(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.root_dir = Path('./test_dir')
        cls.create_test_dir_tree(cls.root_dir)
    # end setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
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

    def test_dirtraverser(self) -> None:
        traverser = DirTraverser(self.root_dir, ignore_hidden=False)
        actual_dirs = set()
        for dir in traverser:
            actual_dirs.add(dir)
        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        self.assertEqual(expected_dirs, actual_dirs)
        return
    # end trest_dirtraverser()

    def test_filetraverser(self) -> None:
        traverser = FileTraverser(self.root_dir, ignore_hidden=False)
        actual_files = set()
        for file in traverser:
            actual_files.add(file)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        self.assertEqual(expected_files, actual_files)
        return
    # end test_filetraverser()

    def test_traverse_only_dirs(self) -> None:
        traverser = Traverser(self.root_dir, is_file_iterator=False, ignore_hidden={'dirs': False, 'files': False})
        actual_dirs = set()
        for dir in traverser:
            actual_dirs.add(dir)

        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2', self.root_dir / '.dir3', self.root_dir / '.dir4', self.root_dir / 'dir2' / '.dir2_3'])
        self.assertEqual(expected_dirs, actual_dirs)
        return
    # end test_traverse_only_dirs()

    def test_traverse_only_dirs_ignore_hidden(self) -> None:
        traverser = Traverser(self.root_dir, is_file_iterator=False)
        actual_dirs = set()
        for dir in traverser:
            actual_dirs.add(dir)

        expected_dirs = set([self.root_dir, self.root_dir / 'dir1', self.root_dir / 'dir2', self.root_dir / 'dir2' / 'dir2_1', self.root_dir / 'dir2' / 'dir2_2'])
        self.assertEqual(expected_dirs, actual_dirs)
        return
    # end test_traverse_only_dirs_ignore_hidden()

    def test_traverse_only_files(self) -> None:
        traverser = Traverser(self.root_dir, is_dir_iterator=False, ignore_hidden={'dirs': False, 'files': False})
        actual_files = set()
        for file in traverser:
            actual_files.add(file)

        expected_files = set([self.root_dir / 'dir1' / 'file1_1', self.root_dir / 'dir1' / 'file1_2', self.root_dir / 'dir1' / 'file_1_3', self.root_dir / 'dir1' / '.file1_4', self.root_dir / 'dir1' / '.file1_5', self.root_dir / 'dir2' / 'dir2_1' / 'file2_1', self.root_dir / '.dir4' / '.file4_1'])
        self.assertEqual(expected_files, actual_files)
        return
    # end test_traverse_only_files()

    def test_traverse_only_files_ignore_hidden(self) -> None:
        traverser = Traverser(self.root_dir, is_dir_iterator=False)
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
        expected: set[Path] = expected_dirs | expected_files
        self.assertEqual(expected, actual_files)
        return
    # end test_traverse_only_files()

# end class TestTraverser

if __name__ == '__main__':
    log = GlobalLogger()
    log.configure(log_dir = Path(__file__).parent,
                 log_filename = 'traverser.log',
                 log_level = logging.DEBUG,
                 log_to_console = True)
    unittest.main()
