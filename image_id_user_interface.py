from pywebio.input import input, ACTIONS
from pywebio.output import put_image, put_buttons, put_text
from pywebio.session import set_scope, get_scope
from pathlib import Path
import os

class Faces:
    def __init__(self, image_dir):
        self.image_dir = Path(image_dir)
        self.image_files = sorted(self.image_dir.glob('*.jpg'))
        self.current_index = 0

    def get_next_image(self, current_name):
        self.current_index = (self.current_index + 1) % len(self.image_files)
        return self.load_image(self.current_index)

    def get_prev_image(self, current_name):
        self.current_index = (self.current_index - 1) % len(self.image_files)
        return self.load_image(self.current_index)

    def load_image(self, index):
        with open(self.image_files[index], 'rb') as file:
            return file.read()

class ImageNavigator:
    # ... (rest of the ImageNavigator class as before)

# Usage:
if __name__ == "__main__":
    faces = Faces('images')  # Assumes images are in a directory named 'images'

    # Getting the initial image
    initial_image_data = faces.load_image(faces.current_index)

    # Creating an ImageNavigator instance, passing in the Faces methods as callbacks
    image_navigator = ImageNavigator(faces.get_next_image, faces.get_prev_image)
    image_navigator.start(initial_image_data)
