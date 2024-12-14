import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class ImageLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Loader")
        self.root.geometry("1940x1080+0+0")  # Set position to top-left corner of the screen

        # Create a container frame to hold the main content and footer
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Create the canvas to hold the images
        self.canvas_frame = tk.Frame(self.main_frame)  # Frame to hold the canvas and scrollbar
        self.canvas_frame.pack(side="top", fill="both", expand=True)

        # Create a Canvas widget
        self.main_pane = tk.Canvas(self.canvas_frame, bg="white", width=1920, height=980)
        self.main_pane.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar for the Canvas
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.main_pane.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.main_pane.configure(yscrollcommand=self.scrollbar.set)

        # Draw a light blue box covering the left half of the main pane
        self.main_pane.create_rectangle(0, 0, 960, 1080, fill="lightblue", outline="lightblue")

        # Draw a thin vertical white bar in the middle
        self.main_pane.create_rectangle(480, 0, 485, 1080, fill="white", outline="white")

        # Create the footer frame with buttons
        self.footer_frame = tk.Frame(self.root, bg="gray", height=100)
        self.footer_frame.pack(side="bottom", fill="x")

        # Load button
        self.load_button = tk.Button(self.footer_frame, text="Load", command=self.load_images)
        self.load_button.pack(side="left", padx=20)

        # Export button (now prints images as requested)
        self.export_button = tk.Button(self.footer_frame, text="Export", command=self.export_images)
        self.export_button.pack(side="right", padx=20)

        # List to hold references to images so they don't get garbage collected
        self.image_references = []
        self.images = []  # Store the image details for drag and drop
        self.dragging_image = None  # Store the image currently being dragged

    def load_images(self):
        folder_path = filedialog.askdirectory()  # Open dialog to choose folder
        if folder_path:
            self.populate_images(folder_path)

    def populate_images(self, folder_path):
        # Clear the main pane
        self.main_pane.delete("all")

        # Redraw the light blue box after clearing the canvas
        self.main_pane.create_rectangle(0, 0, 960, 1080, fill="lightblue", outline="lightblue")

        # Redraw the vertical white bar in the middle
        self.main_pane.create_rectangle(480, 0, 485, 1080, fill="white", outline="white")

        # Get all image files in the folder
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
        x_offset = 985  # Start in the middle of the pane (right side)
        y_offset = 0
        max_row_width = 1920  # Max width (right half of the screen)
        image_width = 300  # Image width
        image_height = 200  # Image height

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(folder_path, image_file)
            img = Image.open(image_path)
            img.thumbnail((image_width, image_height))  # Resize to fit within a smaller area
            img_tk = ImageTk.PhotoImage(img)

            # Store the image details for drag-and-drop
            img_id = self.main_pane.create_image(x_offset, y_offset, image=img_tk, anchor="nw")
            self.images.append({
                'id': img_id,
                'filename': image_path,
                'image': img_tk,
                'x': x_offset,
                'y': y_offset
            })

            # Store the image reference to prevent garbage collection
            self.image_references.append(img_tk)

            # Bind drag and drop events to the image
            self.make_image_draggable(img_id)

            # Update offsets for next image
            x_offset += (image_width + 10)  # Move horizontally by the image width
            if x_offset + image_width > max_row_width:
                # If the image goes beyond the pane width, move to the next row
                x_offset = 985  # Reset to the middle (right side)
                y_offset += image_height + 10  # Move down to the next row

        # Draw a light blue box covering the left half of the main pane
        extended_rect1 = self.main_pane.create_rectangle(0, 0, 960, y_offset-5, fill="lightblue", outline="lightblue")
        # Draw a thin vertical white bar in the middle
        extended_rect2 = self.main_pane.create_rectangle(480, 0, 485, y_offset-5, fill="white", outline="white")
        # Make sure the images are always on top by lowering the rectangles to the back
        self.main_pane.tag_lower(extended_rect2, "all")
        self.main_pane.tag_lower(extended_rect1, "all")

        # Update the scroll region of the canvas to enable vertical scrolling
        self.main_pane.config(scrollregion=self.main_pane.bbox("all"))

    def export_images(self):
        # Separate the images into left and right sections based on their x values
        left_images = [img for img in self.images if img['x'] < 480]
        right_images = [img for img in self.images if img['x'] >= 480 and img['x'] < 960]

        # Sort the images in each section by their y value in descending order
        left_images_sorted = sorted(left_images, key=lambda img: img['y'], reverse=True)
        right_images_sorted = sorted(right_images, key=lambda img: img['y'], reverse=True)

        # Print the images from the left section
        print("Images in the left section (x < 480):")
        for img in left_images_sorted:
            print(f"Image {img['filename']} at x={img['x']}, y={img['y']}")

        # Print the images from the right section
        print("Images in the right section (x >= 480 < 960):")
        for img in right_images_sorted:
            print(f"Image {img['filename']} at x={img['x']}, y={img['y']}")

    def on_image_drag(self, event, image_id):
        # Get the current vertical scroll position
        scroll_y = self.main_pane.yview()[0] * self.main_pane.bbox("all")[3]  # The vertical scroll position multiplied by the canvas height

        # Adjust the event coordinates by the scroll position
        adjusted_y = event.y + scroll_y  # Adjust the y-coordinate for scrolling

        # Move the image based on the adjusted coordinates
        self.main_pane.coords(image_id, event.x, adjusted_y)

        # Update the image position in the list
        for img in self.images:
            if img['id'] == image_id:
                img['x'] = event.x
                img['y'] = adjusted_y  # Update the y position
                break

    def on_image_release(self, event, image_id):
        # Update the final position of the image after it is released
        for img in self.images:
            if img['id'] == image_id[0]:
                img['x'] = event.x
                img['y'] = event.y
                break

    def make_image_draggable(self, image_id):
        # Bind mouse events to make the image draggable
        self.main_pane.tag_bind(image_id, "<ButtonPress-1>", self.start_drag)
        self.main_pane.tag_bind(image_id, "<B1-Motion>", self.on_drag)
        self.main_pane.tag_bind(image_id, "<ButtonRelease-1>", self.on_release)

    def start_drag(self, event):
        # Get the current vertical scroll position
        scroll_y = self.main_pane.yview()[0] * self.main_pane.bbox("all")[3]  # The vertical scroll position multiplied by the canvas height

        # Adjust the event coordinates by the scroll position
        adjusted_y = event.y + scroll_y  # Adjust the y-coordinate for scrolling

        # Identify the image being clicked to start dragging
        image_id = self.main_pane.find_closest(event.x, adjusted_y)

        self.dragging_image = image_id

        # Start dragging by adjusting the initial position
        self.on_image_drag(event, image_id)

    def on_drag(self, event):
        if self.dragging_image:
            self.on_image_drag(event, self.dragging_image)

    def on_release(self, event):
        if self.dragging_image:
            self.on_image_release(event, self.dragging_image)
            self.dragging_image = None


# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLoaderApp(root)
    root.mainloop()
