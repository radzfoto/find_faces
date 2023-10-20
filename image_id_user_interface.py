from typing import Callable
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
from pywebio.input import input
from pywebio.output import put_image, put_buttons, put_text
from pywebio.platform.tornado import start_server
from traverser import Traverser
from global_logger import GlobalLogger

class NameStorer:
    def __init__(self) -> None:
        self._names: list[str] = []
    # end __init__()

    def on_name(self, name: str) -> None:
        self._names.append(name)
    # end on_name()

    def get_names(self) -> list[str]:
        return self._names
    # end get_names()
# end class NameStorer()

class ImageNavigator:
    def __init__(self, traverser: Traverser, on_name: Callable[[str], None]) -> None:
        self.logging_info = GlobalLogger()
        self.log = self.logging_info.global_logger

        self.traverser: Traverser = traverser
        self.on_name: Callable[[str], None] = on_name
        self.current_image_path: Path = Path()

    def image_path_to_base64(self, image_path: Path, fmt) -> str:
        with Image.open(image_path.as_posix()) as image:
            buffered = BytesIO()
            image.save(buffered, format=fmt)
            return base64.b64encode(buffered.getvalue()).decode()
    # end image_path_to_base64()

    def pil_to_bytes(self, image: Image.Image, format: str = 'JPEG') -> bytes:
        with BytesIO() as buffer:
            image.save(buffer, format=format)
            return buffer.getvalue()

    def display_image(self) -> None:
        self.log.info(f'Displaying: {self.current_image_path.as_posix()}')
        image: Image.Image = Image.open(self.current_image_path.as_posix())
        assert image is not None, 'Unable to open image file'
        ext = (self.current_image_path.suffix).lower()
        self.log.debug(f'File extension: {ext}')
        fmt=''
        if ext in ['.jpg', '.jpeg']:
            ext = 'jpg'
            fmt = 'JPEG'
        elif ext in ['.png']:
            ext = 'png'
            fmt = 'PNG'
        else:
            assert False, f'ERROR: Invalid file type: {ext}'
        # image_base64 = self.image_path_to_base64(self.current_image_path, fmt)
        image_bytes = self.pil_to_bytes(image, format=fmt)
        put_image(image_bytes, format=ext)
    # end display_image()

    def start(self):
        # self.current_image_data = initial_image_data
        action = 'Next'
        while True:
            if action == 'Next':
                try:
                    self.current_image_path: Path = next(self.traverser)
                    self.log.debug(f'Received from traverser: {self.current_image_path}')
                except StopIteration:
                    break
            elif action == 'Quit':
                break
            else:
                break
            self.display_image()
            name = input("Who is in the picture?", type="text")
            self.on_name(str(name))
            action = put_buttons(['Next', 'Quit'], onclick=lambda x: x)

# end class ImageNavigator

def app():
    images_dir: Path = Path().home() / "pics_test/test_small"
    image_file_types_glob_list: list[str] = ['*.jpg', '*.jpeg', '*.png']
    traverser = Traverser(root_dir=images_dir, is_dir_iterator=False, match_files=image_file_types_glob_list)

    name_storer = NameStorer()

    image_navigator = ImageNavigator(traverser=traverser, on_name=name_storer.on_name)
    image_navigator.start()
    name_list: list[str] = name_storer.get_names()
    for name in name_list:
        print(name)
# end app()

def main() -> None:
    logger_config = GlobalLogger(log_dir=Path(__file__).parent,
                                        log_filename='image_UI.log',
                                        log_level=GlobalLogger.DEBUG,
                                        log_messages_to_console=True)
    log = logger_config.global_logger
    start_server(app, port=8080, open_webbrowser=True)
    return
# end main()

if __name__ == "__main__":
    main()
