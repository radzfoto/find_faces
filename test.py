from pathlib import Path

p = Path("image.jpg.json")
basename_without_last_suffix = p.stem
last_suffix = p.suffix

# To get "image.jpg"
original_name = f"{basename_without_last_suffix}{last_suffix}"
print(original_name)  # Output: "image.jpg.json"
print(basename_without_last_suffix)
