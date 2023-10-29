from pathlib import Path
import shutil
from traverser import DirTraverser

def is_hidden(path: Path) -> bool:
    return path.name.startswith('.')
# end is_hidden()

def remove_metadata(root_dir: Path, dirnames_to_delete: list[Path] = [Path('.faces')]) -> None:

    dir_traverser = DirTraverser(root_dir, ignore_hidden=False)
    for dir_path in dir_traverser:
        if dir_path in dirnames_to_delete:
            if is_hidden(dir_path):
                print(f'Removing metadata directory: {dir_path.as_posix()}')
                shutil.rmtree(dir_path)

    # print(f'Removing from: {dir_path.as_posix()}')
    # for fp in dir_path.iterdir():
    #     if fp.is_dir() and (fp.name not in dirnames_to_delete) and (not is_hidden(fp)):
    #         remove_metadata(fp, dirnames_to_delete, extensions_to_delete)
    #     elif fp.is_file() and (fp.suffix in extensions_to_delete):
    #         fp.unlink()
    #     else:
    #         pass
    #     #end if
    # # end for
    return
# end remove_metadata

def main() -> None:
    root_dir: Path = Path().home() / Path("pics_test/test_small")
    
    print('Start removing metadata.')
    remove_metadata(dir_path=root_dir, 
                    dirnames_to_delete=[Path('.faces')])
    print('Completed removing metadata')
    return
# end main

if __name__ == '__main__':
    main()
