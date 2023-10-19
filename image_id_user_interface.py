from typing import Callable, Any
from pathlib import Path
from pywebio.input import input
from pywebio.output import put_image, put_buttons, put_text
from pywebio.platform.tornado import start_server
from traverser import Traverser
from global_logger import GlobalLogger

# class ImageNavigator:
#     def __init__(self, traverser, on_name):
#         logging_info = GlobalLogger()
#         log = logging_info.global_logger

#         self.traverser = traverser
#         self.on_name = on_name
#         self.current_image_data = None

#     def display_image(self):
#         put_image(self.current_image_data, format='jpg')

#     def start(self, initial_image_data):
#         self.current_image_data = initial_image_data
#         while True:
#             self.display_image()
#             name = input("Who is in the picture?", type="text")
#             self.on_name(name)
#             action = put_buttons(['Next', 'Quit'], onclick=lambda x: x)
#             if action == 'Next':
#                 self.current_image_data = next(self.traverser)
#             elif action == 'Quit':
#                 break


class ImageNavigator:
    def __init__(self, traverser: Traverser, on_name: Callable[[Path], None]) -> None:
        logging_info = GlobalLogger()
        log = logging_info.global_logger

        self.traverser: Traverser = traverser
        self.on_name = on_name
        self.current_image_data = Path()
    # end __init__()

    def scan_imagefiles(self) -> None:
        # for image_filepath in self.traverser:
        path: Path = next(self.traverser)
        while path != Path():
            self.on_name(path)
            try:
                path = next(self.traverser)
            except StopIteration:
                break
    # end scan_imagefiles()
# end class ImageNavigator

class NameStorer:
    def __init__(self) -> None:
        self._names: list[Path] = []
    # end __init__()

    def on_name(self, name: Path) -> None:
        self._names.append(name)
    # end on_name()

    def get_names(self) -> list[Path]:
        return self._names
    # end get_names()
# end class NameStorer()

def app():
    images_dir: Path = Path().home() / Path("pics_test/test_small")
    image_file_types_glob_list: list[str] = ['*.jpg', '*.jpeg', '*.png']
    name_storer = NameStorer()
    traverser = Traverser(images_dir, match_files=image_file_types_glob_list)
    test_traverser = Traverser(images_dir, match_files=image_file_types_glob_list)
    print('---------')
    for p in test_traverser:
        print(p)
    print('---------')
    image_navigator = ImageNavigator(traverser, name_storer.on_name)
    image_navigator.scan_imagefiles()
    name_list = name_storer.get_names()
    for path in name_list:
        print(path)
    # image_navigator.start(next(traverser))
# end app()

def main() -> None:
    logger_config = GlobalLogger(log_dir=Path(__file__).parent,
                                        log_filename='image_UI.log',
                                        log_level=GlobalLogger.DEBUG,
                                        log_messages_to_console=True)
    log = logger_config.global_logger
    app()
    # start_server(app, port=8080, open_webbrowser=True)
    return
# end main()

if __name__ == "__main__":
    main()

# TRY THIS FOR ASYNC get_names
# import threading
# import time

# class AnotherClass:
#     # ... rest of your code ...

#     def get_names(self):
#         return self.names

# def name_retrieval(another_class):
#     while True:
#         names = another_class.get_names()
#         print(names)  # Or process the names as needed
#         time.sleep(10)  # Sleep for 10 seconds before retrieving again

# another_class = AnotherClass()
# # Assuming image_navigator and traverser have been created and started
# retrieval_thread = threading.Thread(target=name_retrieval, args=(another_class,))
# retrieval_thread.start()

# OR THIS

# import asyncio

# class AnotherClass:
#     # ... rest of your code ...

#     def get_names(self):
#         return self.names

# async def name_retrieval(another_class):
#     while True:
#         names = another_class.get_names()
#         print(names)  # Or process the names as needed
#         await asyncio.sleep(10)  # Sleep for 10 seconds before retrieving again

# another_class = AnotherClass()
# # Assuming image_navigator and traverser have been created and started
# asyncio.run(name_retrieval(another_class))


