import streamlit as st
from PIL import Image
from traverser import Traverser
from pathlib import Path

# Initialize Traverser
images_dir = Path().home() / "pics_test/test_small"
image_file_types_glob_list = ['*.jpg', '*.jpeg', '*.png']
traverser = Traverser(root_dir=images_dir, is_dir_iterator=False, match_files=image_file_types_glob_list)

st.title("Image Navigator")

# Initialize variables
name_list = []

# Main loop
while True:
    try:
        image_path = next(traverser)
    except StopIteration:
        st.write("No more images.")
        break

    # Display the image
    image = Image.open(image_path)
    st.image(image, caption=image_path.name, use_column_width=True)

    # Input for the name
    name = st.text_input("Who is in the picture?", key=image_path.as_posix())

    # Buttons
    if st.button("Next", key=image_path.as_posix()):
        if name:
            name_list.append(name)
            st.write(f"Stored names: {name_list}")
        else:
            st.warning("Please enter a name.")

    if st.button("Quit", key=image_path.as_posix()):
        break

# Display stored names
st.write(f"Final stored names: {name_list}")
