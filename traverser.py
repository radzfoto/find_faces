from abc import ABC, abstractmethod
from typing import Pattern, Iterator, Generator
from pathlib import Path
import copy
import re
import fnmatch
import json

class JSONTraverserEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, list):
            if all(isinstance(item, Path) for item in obj):
                return super(JSONTraverserEncoder, self).encode({"type": "Path", "data": [str(p) for p in obj]})
            elif all(isinstance(item, str) for item in obj):
                return super(JSONTraverserEncoder, self).encode({"type": "str", "data": obj})
        return super(JSONTraverserEncoder, self).encode(obj)

def json_traverser_decoder(obj):
    if "type" in obj and "data" in obj:
        if obj["type"] == "Path":
            return [Path(p) for p in obj["data"]]
        elif obj["type"] == "str":
            return obj["data"]
    return obj

# class AbstractTraverser(ABC):

#     def __init__(self,
#                  root_dir: Path,
#                  ignore_hidden: bool,
#                  match_list: list[str],
#                  ignore_list: list[str]
#                  ) -> None:

#         # ENABLE DEBUG MODE
#         self.debug: bool = True

#         self.__saved_root_dir: Path = root_dir
#         self.__saved_match_list: list[str] = match_list
#         self.__saved_ignore_hidden: bool = ignore_hidden
#         self.__saved_ignore_list: list[str] = ignore_list

#         match_pattern: Pattern[str] = self.__make_pattern(self.__saved_match_list)
#         self.__saved_match: Pattern[str] = match_pattern

#         self.reset()
#     # end __init__()

#     def reset(self) -> None:
#         print("Entering AbstractTraverser reset")
#         if not self.__saved_root_dir.is_dir():
#             raise FileNotFoundError (f"Starting directory is invalid or does not exist: {self.__saved_root_dir}")
#         self._root_dir = self.__saved_root_dir
#         self._ignore_list: list[str] = self.__saved_ignore_list
#         self._ignore_hidden: bool = self.__saved_ignore_hidden
#         self._match_list: list[str] = self.__saved_match_list
#         self._match: Pattern[str] = self.__saved_match
#     # end reset()

#     def __make_pattern(self, glob_pattern_list: list[str]) -> Pattern[str]:
#         regex_parts: list[str] = [fnmatch.translate(part) for part in glob_pattern_list]

#         regex_pattern: str = '|'.join(regex_parts)

#         regex: Pattern[str] = re.compile(regex_pattern, re.IGNORECASE)

#         return regex
#     # end __make_pattern()

#     def __get_files_in_curr_dir(self, curr_dir)-> list[Path]:
#             files_in_curr_dir: list[Path] = []
#             must_append: bool = False
#             for path in curr_dir.iterdir():
#                 must_append = path.is_file()
#                 must_append = must_append and (path.name not in self._ignore_list)
#                 must_append = must_append and (self._match.match(string=path.name) is not None)
#                 must_append = must_append and ((self._ignore_hidden and not path.name.startswith('.')) or (not self._ignore_hidden))
#                 if must_append:
#                     files_in_curr_dir.append(path)
#             return files_in_curr_dir
#     # end __get_next_file_in_curr_dir()

#     def __iter__(self) -> Generator[Path, None, None]:
#         return self._iterate()
#     # end __iter__()

#     @abstractmethod
#     def _iterate(self) -> Generator[Path, None, None]:
#         pass
#     # end _iterate()

# # end class AbstractTraverser()

# class DirTraverser(AbstractTraverser):

#     def __init__(self,
#                  root_dir: Path,
#                  ignore_hidden: bool = True,
#                  match_list: list[str] = ['*'],
#                  ignore_list: list[str] = ['.DS_Store', '.Trash']
#                  ) -> None:
#         super().__init__(root_dir, ignore_hidden, match_list, ignore_list)
#         self.reset()
#         return
#     # end __init__()

#     def reset(self) -> None:
#         print("Entering DirTraverser reset")
#         super().reset()
#         self._directories: list[Path] = [self._root_dir]
#         self._current_dir: Path = Path()
#         return
    
#     def __deepcopy__(self, memo):
#         new_instance = DirTraverser(
#             root_dir=self.__saved_root_dir,
#             ignore_hidden=self.__saved_ignore_hidden,
#             match_list=self.__saved_match_list,
#             ignore_list=self.__saved_ignore_list
#         )
#         return new_instance
    
#     def copy(self):
#         return self.__deepcopy__({})

#     def _iterate(self) -> Generator[Path, None, None]:
#         while len(self._directories) > 0:
#             self._current_dir = self._directories.pop(0)
#             dir_name : str = self._current_dir.name
#             if dir_name in self._ignore_list or \
#                            (self._ignore_hidden and dir_name.startswith('.')):
#                 continue
#             if self._match.match(string=dir_name):
#                 dirs_at_this_level: list[Path] = []
#                 for path in self._current_dir.iterdir():
#                     if path.is_dir() and (path.name not in self._ignore_list) and \
#                        ((self._ignore_hidden and not (path.name).startswith('.')) or (not self._ignore_hidden)):
#                         dirs_at_this_level.append(path)
#                 self._directories[:0] = dirs_at_this_level  # Insert new dirs at beginning, needed to reduce memory used during tree traversal since this causes a depth first emission of dirs
#                 self._files_indicator = False
#             yield self._current_dir
#     # end _iterate()

# # end class DirTraverser()

# class FileTraverser(AbstractTraverser):

#     def __init__(self,
#                  root_dir: Path,
#                  dir_traverser: DirTraverser | None, # If dir_traverser has the same ignore/match/etc, then leave as None. Otherwise, create a unique dir_traverser instance
#                  ignore_hidden: bool = True,
#                  match_list: list[str] = ['*'],
#                  ignore_list: list[str] = ['.DS_Store', '.Trash'],
#                  emit_dirs: bool = False
#                  ) -> None:

#         # ENABLE DEBUG MODE
#         super().__init__(root_dir, ignore_hidden, match_list, ignore_list)

#         self.__saved_dir_traverser: DirTraverser
#         self.__saved_has_dir_traverser: bool = dir_traverser is not None
#         if dir_traverser is not None:
#             self.__saved_dir_traverser: DirTraverser = dir_traverser

#         self.__saved_emit_dirs: bool = emit_dirs

#         # self.__saved_files_in_curr_dir: list[Path] = []

        
#         self.reset()
#         return
#     # end __init__()

#     def reset(self) -> None:
#         print("Entering FileTraverser reset")
#         super().reset()
#         print(self.__saved_emit_dirs)
#         if self.__saved_has_dir_traverser:
#             self.__dir_traverser: DirTraverser = self.__saved_dir_traverser.copy()
#         else:
#             self.__dir_traverser = DirTraverser(self.__saved_root_dir,
#                                     self.__saved_ignore_hidden,
#                                     self.__saved_match_list,
#                                     self.__saved_ignore_list)
#         self._emit_dirs: bool = self.__saved_emit_dirs
#         # self._files_in_curr_dir: list[Path] = self.__saved_files_in_curr_dir
#         return
#     # end reset()

#     def __deepcopy__(self, memo):
#         new_instance = FileTraverser(
#             root_dir=self.__saved_root_dir,
#             dir_traverser=copy.deepcopy(self.__saved_dir_traverser, memo),
#             ignore_hidden=self.__saved_ignore_hidden,
#             match_list=self.__saved_match_list,
#             ignore_list=self.__saved_ignore_list,
#             emit_dirs=self.__saved_emit_dirs
#         )
#         return new_instance

#     def _iterate(self) -> Generator[Path, None, None]:
#         for curr_dir in self.__dir_traverser:
#             if self._emit_dirs:
#                 yield curr_dir

#             file_list: list[Path] = self.__get_files_in_curr_dir(curr_dir)
#             for file in file_list:
#                 yield file
#     # end _iterate

# # end class DirTraverser()

# class Traverser:
#     """
#     USAGE:
#         instantiate a Traverser object such as traverer = Traverser(/dirtree/to/traverse)

#         Travers is an iterator object that yields either all the directories in
#         the tree or all the files in the tree, or both, depending the is_dir_iterator and
#         is_file_iterator parameters (see below).

#         ignore_hidden['dirs'] and ignore_hidden['files'] will ignore hidden directories and
#         hidden files respectively. Note that these boolean parameters override the match and ignore
#         glob lists if there is a conflict.
        
#         match_dirs, match_files, ignore_list['dirs], and ig and ignore_hidden_files are each a list of glob expressions
#         such as ['*.jpg', '*.jpeg']
        
#         match_dirs and match_files are each a list of glob expressions such as ['*.jpg', '*.jpeg'].
#         Files or directories that match any of glob patterns in the list will be matched.
#     """

#     def __init__(self,
#                  root_dir: Path,
#                  ignore_hidden: dict[str, bool] = {'dirs': True, 'files': True},
#                  match_list: dict[str, list[str]] = {'dirs': ['*'], 'files': ['*']},
#                  ignore_list: dict[str, list[str]] = {'dirs': ['.DS_Store', '.Trash'], 'files': ['.DS_Store']},
#                  is_dir_iterator: bool = True,
#                  is_file_iterator: bool = True,
#                  ) -> None:

#         # ENABLE DEBUG MODE
#         #self.debug: bool = True

#         self.__saved_root_dir: Path = root_dir
#         self.__saved_ignore_hidden: dict[str, bool] = ignore_hidden
#         self.__saved_match_list: dict[str, list[str]] = match_list
#         self.__saved_ignore_list: dict[str, list[str]] = ignore_list
#         self.__saved_is_dir_iterator: bool = is_dir_iterator
#         self.__saved_is_file_iterator: bool = is_file_iterator

#         self.reset()
#     # end __init__()

#     def reset(self) -> None:
#         self.__root_dir: Path = self.__saved_root_dir
#         self.__is_dir_iterator: bool = self.__saved_is_dir_iterator
#         self.__is_file_iterator: bool = self.__saved_is_file_iterator
#         self.__ignore_hidden: dict[str, bool] = self.__saved_ignore_hidden
#         self.__match_list: dict[str, list[str]] = self.__saved_match_list
#         self.__ignore_list: dict[str, list[str]] = self.__saved_ignore_list

#         self.__dir_traverser = DirTraverser(self.__root_dir,
#                                             self.__ignore_hidden['dirs'],
#                                             self.__match_list['dirs'],
#                                             self.__ignore_list['dirs'])
        
#         if self.__is_file_iterator:
#             self.__file_traverser = FileTraverser(self.__root_dir,
#                                                 self.__dir_traverser,
#                                                 self.__ignore_hidden['files'],
#                                                 self.__match_list['files'],
#                                                 self.__ignore_list['files'],
#                                                 emit_dirs=self.__is_dir_iterator
#                                         )
#     # end reset()

#     def __deepcopy__(self, memo):
#         return Traverser(
#             root_dir=self.__saved_root_dir,
#             ignore_hidden=self.__saved_ignore_hidden,
#             match_list=self.__saved_match_list,
#             ignore_list=self.__saved_ignore_list,
#             is_dir_iterator=self.__saved_is_dir_iterator,
#             is_file_iterator=self.__saved_is_file_iterator
#         )

#     def __iter__(self) -> Generator[Path, None, None]:
#         return self.__iterate()

#     def __iterate(self) -> Generator[Path, None, None]:
#         if self.__is_file_iterator:
#             for file in self.__file_traverser:
#                 yield file
#         else:
#             for dir in self.__dir_traverser:
#                 yield dir
#     # end _iterate_files(self)

# # end class Traverser()

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
    #        is_dir_iterator and is_file_iterator together allow iteration on only dirs in dir tree,
    #        only files in dir tree, or both.
    #       
    #        match['dirs'] and match_files are each a list of single glob expressions such as ['*.jpg', '*.jpeg'].
    #        Files or directories that match any of glob patterns in the list will be matched

    def __init__(self,
                 root_dir: Path,
                 match_dirs: list[str] = ['*'],
                 match_files: list[str] = ['*'],
                 ignore_hidden: dict[str, bool] = {'dirs': True, 'files': True},
                 ignore_list: dict[str, list[str]] = {'dirs': ['.DS_Store', '.Trash'], 'files': ['.DS_Store']},
                 is_dir_iterator: bool = True,
                 is_file_iterator: bool = True,
                 ) -> None:
        self.__saved_root_dir: Path = root_dir
        self.__saved_match_dirs: list[str] = match_dirs
        self.__saved_match_files: list[str] = match_files
        self.__saved_ignore_hidden: dict[str, bool] = ignore_hidden
        self.__saved_ignore_list: dict[str, list[str]] = ignore_list
        self.__saved_is_dir_iterator: bool = is_dir_iterator
        self.__saved_is_file_iterator: bool = is_file_iterator
        # self._is_iterator: dict[str, bool] = {'dirs': is_dir_iterator, 'files': is_file_iterator}
        # self.__saved_is_iterator: dict[str, bool] = self._is_iterator

        self.reset()
    # end __init__()

    def reset(self) -> None:
        self._is_dir_iterator: bool = self.__saved_is_dir_iterator
        self._is_file_iterator: bool = self.__saved_is_file_iterator
        # self._is_iterator: dict[str,bool] = self.__saved_is_iterator
        self._directories: list[Path] = [self.__saved_root_dir]
        self._current_dir: Path = Path()
        self._files_in_current_dir: list[Path] = []
        self._files_indicator:bool = False
        self._ignore_dirs: list[str] = self.__saved_ignore_list['dirs']
        self._ignore_files: list[str] = self.__saved_ignore_list['files']

        self._ignore_hidden_files: bool = self.__saved_ignore_hidden['files']
        self._ignore_hidden_dirs: bool =  self.__saved_ignore_hidden['dirs']

        match_dir_pattern: Pattern[str] = self.__make_pattern(self.__saved_match_dirs)
        match_file_pattern: Pattern[str] = self.__make_pattern(self.__saved_match_files)
        self._match_dirs: Pattern[str] = match_dir_pattern
        self._match_files: Pattern[str] = match_file_pattern

        if self._is_file_iterator and not self._is_dir_iterator:
            self._get_next_dir() # Initialize file iterator
    # end reset()

    def __make_pattern(self, glob_pattern_list: list[str]) -> Pattern[str]:
        regex_parts: list[str] = [fnmatch.translate(part) for part in glob_pattern_list]

        regex_pattern: str = '|'.join(regex_parts)

        regex: Pattern[str] = re.compile(regex_pattern, re.IGNORECASE)

        return regex
    # end __make_pattern()

    def _get_next_dir(self) -> Path:
        while self._directories:
            self._current_dir = self._directories.pop(0)
            
            if not self._current_dir.exists():  # Handle changes to directory structure during traversal
                continue
            dir_name : str = self._current_dir.name
            if dir_name in self._ignore_dirs or \
                           (self._ignore_hidden_dirs and dir_name.startswith('.')):
                continue

            if self._match_dirs.match(string=dir_name):
                dirs_at_this_level: list[Path] = []
                for path in self._current_dir.iterdir():
                    if path.is_dir() and (path.name not in self._ignore_dirs) and \
                       ((self._ignore_hidden_dirs and not (path.name).startswith('.')) or (not self._ignore_hidden_dirs)):
                        dirs_at_this_level.append(path)
                self._directories[:0] = dirs_at_this_level  # Insert new dirs at beginning, needed to reduce memory used during tree traversal since this causes a depth first emission of dirs

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
        assert self._is_file_iterator, f'{self.__class__.__name__} instance has disabled file iteration.'

        if self._current_dir == Path():
            if self._is_dir_iterator:
                return self._iterate_dirs()
            else:
                self._get_next_dir()

        next_file: Path = self._get_next_file()

        if next_file != Path():
            return next_file
        else:
            if self._is_dir_iterator:
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
        if self._is_dir_iterator and not self._is_file_iterator:
            return self._iterate_dirs()
        elif not self._is_dir_iterator and self._is_file_iterator:
            return self._iterate_files()
        elif self._is_dir_iterator and self._is_file_iterator:
            return self._iterate_files()
        else:
            raise StopIteration
    # end __next__()

    def next_dir(self) -> Path:
        return self._get_next_dir()
    # end next_dir()

    def next_file(self) -> Path:
        return self._get_next_file()
    # end next_file()

# end class Traverser()

class SimpleTraverser(Traverser):
    def __init__(self,                 
                 root_dir: Path,
                 ignore_hidden: bool = True,
                 match_list: list[str] = ['*'],
                 ignore_list: list[str] =['.DS_Store', '.Trash'],
                 is_dir_iterator: bool = True,
                 is_file_iterator: bool = True
            ) -> None:
    
        ignore_hidden_both: dict[str, bool] = {'dirs': ignore_hidden, 'files': ignore_hidden}
        match_dirs: list[str] = match_list
        match_files: list[str] = match_list
        ignore_dict_list: dict[str, list[str]] = {'dirs': ignore_list, 'files': ignore_list}
        
        super().__init__(root_dir, match_dirs, match_files, ignore_hidden_both, ignore_dict_list, is_dir_iterator, is_file_iterator)
    # end __init__()
# end class SimpleTraverser()

class DirTraverser(SimpleTraverser):
    def __init__(self,                 
                 root_dir: Path,
                 ignore_hidden: bool = True,
                 match_list: list[str] = ['*'],
                 ignore_list: list[str] =['.DS_Store', '.Trash']
            ) -> None:
        super().__init__(root_dir,
                        ignore_hidden,
                        match_list,
                        ignore_list,
                        is_dir_iterator=True,
                        is_file_iterator=False)
     # end __init__()
# end class DirTraverser()

class FileTraverser(SimpleTraverser):
    def __init__(self,                 
                 root_dir: Path,
                 ignore_hidden: bool = True,
                 match_list: list[str] = ['*'],
                 ignore_list: list[str] =['.DS_Store', '.Trash']
            ) -> None:
        super().__init__(root_dir,
                        ignore_hidden,
                        match_list,
                        ignore_list,
                        is_dir_iterator=False,
                        is_file_iterator=True)
     # end __init__()
# end class FileTraverser()