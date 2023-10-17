from pathlib import Path
import shutil

def is_hidden(path: Path) -> bool:
    return path.name.startswith('.')
# end is_hidden()

def remove_metadata(dir_path: Path, dirnames_to_delete: list[Path], extensions_to_delete: list[str]) -> None:

    for dirname in dirnames_to_delete:
        fp = dir_path / dirname
        if fp.exists() and is_hidden(fp):
            shutil.rmtree(fp)

    print(f'Removing from: {dir_path.as_posix()}')
    for fp in dir_path.iterdir():
        if fp.is_dir() and (fp.name not in dirnames_to_delete) and (not is_hidden(fp)):
            remove_metadata(fp, dirnames_to_delete, extensions_to_delete)
        elif fp.is_file() and (fp.suffix in extensions_to_delete):
            fp.unlink()
        else:
            pass
        #end if
    # end for
    return
# end remove_metadata

def main() -> None:
    root_dir: Path = Path().home() / Path("pics_test/test_small")
    
    print('Start removing metadata.')
    remove_metadata(dir_path=root_dir, 
                    dirnames_to_delete=[Path('.faces')],
                    extensions_to_delete = ['.faces', '.log'])
    print('Completed removing metadata')
    return
# end main

if __name__ == '__main__':
    main()
