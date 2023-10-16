

from pathlib import Path
import re
import fnmatch

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
    #        is None.                                                                                                                     
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
                 ignore_hidden:bool=True,
                 ignore_hidden_files:bool=None,
                 ignore_hidden_dirs:bool=None,
                 ignore_dirs: list[str] = ['.DS_Store'], 
                 ignore_files: list[str] = ['.DS_Store'],
                 is_dir_iterator = False,  # True makes this a file iterator, False makes this a directory iterator
                 gets_files_in_curr_dir = False): # next_file and file iterator only iterate over the current directory

        self._is_dir_iterator = is_dir_iterator
        self._gets_files_in_curr_dir: bool = gets_files_in_curr_dir                                         
        self._directories: list[Path] = [root_dir]                                                                                                          
        self._current_dir: Path = None                                                                                                                 
        self._files_in_current_dir = None                                                                                                        
        self._files_indicator:bool = False                                                                                                            
        self._ignore_dirs:bool = ignore_dirs                                                                                                          
        self._ignore_files:bool = ignore_files   

        if self._is_dir_iterator:
            self._gets_files_in_curr_dir: bool = True   

        if ignore_hidden is not None:                                                                                                                       
            self._ignore_hidden_files = ignore_hidden                                                                                            
            self._ignore_hidden_dirs = ignore_hidden                                                                                             
        else:                                                                                                                 
            self._ignore_hidden_files = (ignore_hidden_files is not None) and ignore_hidden_files                                         
            self._ignore_hidden_dirs =  (ignore_hidden_dirs is not None) and ignore_hidden_dirs                                                
        self._match_dirs = re.compile(fnmatch.translate(match_dirs))                                                                             
        self._match_files = re.compile(fnmatch.translate(match_files))
    # end __init__()                                                                         
                                                                                                                                                
    def _get_next_dir(self):                                                                                                                         
        while self._directories:                                                                                                                
            self._current_dir = self._directories.pop(0)                                                                                         
            dir_name = str(self._current_dir.name)                                                                                               
            if dir_name in self._ignore_dirs or \
                           (self._ignore_hidden_dirs and dir_name.startswith('.')):                                          
                continue                                                                                                                        
            if self._match_dirs.match(dir_name):                                                                                                 
                for path in self._current_dir.iterdir():                                                                                         
                    if path.is_dir() and \
                       (path.name not in self._ignore_dirs) and \
                       not (self._ignore_hidden_dirs and not dir_name.startswith('.')):                                                                     
                        self._directories.append(path)                                                                                          
                self._files_in_current_dir = None                                                                                                
                self._files_indicator = False                                                                                                    
                return self._current_dir                                                                                                         
        return None  
    # end _get_next_dir()                                                                                                                           
                                                                                                                                                
    def _get_next_file(self):                                                                                                           
        if not self._files_indicator:
            if self._current_dir is None:  # This happens if next_file is called before next_dir()
                self._get_next_dir()                                                                                                           
            self._files_in_current_dir = [path for path in self._current_dir.iterdir() \
                                              if path.is_file() and \
                                                 path.name not in self._ignore_files and \
                                                 not (self._ignore_hidden_files and path.name.startswith('.')) and \
                                                 self._match_files.match(path.name)]                                      
            self._files_indicator = True                                                                                                         
        return self._files_in_current_dir.pop(0) if self._files_in_current_dir else None
    # end _get_next_file()

    def __iter__(self):
        return self
    # end __iter__()

    def _iterate_dirs(self):
        next_dir = self._get_next_dir()
        if next_dir is None:
            raise StopIteration
        return next_dir
    # end _iterate_dirs()

    def _iterate_files(self, no_stop_iteration=False):
        next_file = self._get_next_file()
        if self._gets_files_in_curr_dir:
            if next_file is None:
                if no_stop_iteration:
                    return None
                else:
                    raise StopIteration
        else:
            if next_file is not None:
                return next_file

            next_dir = self._get_next_dir()
            while next_dir is not None:
                next_file = self._get_next_file()
                if next_file is not None:
                    return next_file
                next_dir = self._get_next_dir()

            if no_stop_iteration:
                return None
            else:
                raise StopIteration
    # end _iterate_files(self)

    def __next__(self):
        if self._is_dir_iterator:
            return self._iterate_dirs()
        else:
            return self._iterate_files(no_stop_iteration=False)
    # end __next__()

    def next_dir(self):
        return self._get_next_dir()
    # end next_dir()

    def next_file(self):
        if self._gets_files_in_curr_dir:
            return self._get_next_file()
        else:
            return self._iterate_files(no_stop_iteration=True)
    # end next_file()

    # end __next__()
# end class TreeTraverser()

def test():
    traverser = Traverser(Path().home() / Path('pics_test/test_small'),
                                 ignore_hidden=False, is_dir_iterator=True)
    max_dir_count_allowed: int = 50  # For testing to prevent infinite loops and long tests
    max_file_count_allowed: int = 100  # For testing to prevent infinite loops and long tests
    # for dir_counter in range(max_dir_count_allowed):
    #     # Traverse directories
    #     next_dir = traverser.next_dir()
    #     if next_dir is None:
    #         break
    #     print(f"Directory: {next_dir.as_posix()}")

    #     # Traverse files in the current directory
    #     for file_counter in range(max_file_count_allowed):
    #         next_file = traverser.next_file()
    #         if next_file is None:
    #             break
    #         print(f"File: {next_file.as_posix()}")
    
    counter = 0
    for file in traverser:
        print(file.as_posix())
        counter += 1
        if counter > (max_dir_count_allowed*max_file_count_allowed):
            break
    
    return
# end test()

if __name__ == '__main__':
    test()
