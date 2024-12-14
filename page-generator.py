import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class ImageLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Loader")
        self.root.geometry("1920x1080+0+0")  # Set position to top-left corner of the screen

        # Create a container frame to hold the main content and footer
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Create the main pane (right side for images)
        self.main_pane = tk.Canvas(self.main_frame, bg="white", width=960, height=980)  # Right half of the window
        self.main_pane.pack(side="top", fill="both", expand=True)

        # Create the footer frame with buttons
        self.footer_frame = tk.Frame(self.root, bg="gray", height=100)
        self.footer_frame.pack(side="bottom", fill="x")

        # Load button
        self.load_button = tk.Button(self.footer_frame, text="Load", command=self.load_images)
        self.load_button.pack(side="left", padx=20)

        # Export button (does nothing for now)
        self.export_button = tk.Button(self.footer_frame, text="Export", command=self.export_images)
        self.export_button.pack(side="right", padx=20)

        # List to hold references to images so they don't get garbage collected
        self.image_references = []

    def load_images(self):
        folder_path = filedialog.askdirectory()  # Open dialog to choose folder
        if folder_path:
            self.populate_images(folder_path)

    def populate_images(self, folder_path):
        # Clear the main pane
        self.main_pane.delete("all")

        # Get all image files in the folder
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
        x_offset = 965  # Start in the middle of the pane (right side)
        y_offset = 0
        max_row_width = 1920  # Max width (right half of the screen)
        image_width = 150  # Image width
        image_height = 150  # Image height

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)
            img.thumbnail((image_width, image_height))  # Resize to fit within a smaller area
            img_tk = ImageTk.PhotoImage(img)

            # Create an image label in the canvas
            self.main_pane.create_image(x_offset, y_offset, image=img_tk, anchor="nw")

            # Store the image reference to prevent garbage collection
            self.image_references.append(img_tk)

            print(f"{image_path} added at {x_offset}, {y_offset}")

            # Update offsets for next image
            x_offset += (image_width + 10)  # Move horizontally by the image width
            print(f"Incremented X for next image")
            print(f"if {x_offset} + {image_width} > {max_row_width}:")
            if x_offset + image_width > max_row_width:
                print(f"Hit the edge, incremented Y")
                # If the image goes beyond the pane width, move to the next row
                x_offset = 965  # Reset to the middle (right side)
                y_offset += image_height  # Move down to the next row

    def export_images(self):
        pass  # Export functionality not implemented yet

# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLoaderApp(root)
    root.mainloop()
