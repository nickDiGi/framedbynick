import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk


class ImageLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Loader")

        # Create a canvas to hold the columns and make it scrollable
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the canvas
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the three columns inside the canvas
        self.column_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.column_frame, anchor="nw")

        # Create three columns (LabelFrame) for holding images
        self.column1 = tk.LabelFrame(self.column_frame, text="Column 1", width=200, height=300)
        self.column1.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.column2 = tk.LabelFrame(self.column_frame, text="Column 2", width=200, height=300)
        self.column2.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.column3 = tk.LabelFrame(self.column_frame, text="Column 3", width=200, height=300)
        self.column3.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Update the scroll region to accommodate all the columns
        self.column_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Button frame at the bottom, outside the canvas
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10, fill=tk.X)

        # Load button
        self.load_button = tk.Button(self.button_frame, text="Load", command=self.load_images)
        self.load_button.grid(row=0, column=0, padx=10)

        # Export button (does nothing for now)
        self.export_button = tk.Button(self.button_frame, text="Export", command=self.export_images)
        self.export_button.grid(row=0, column=1, padx=10)

        # A reference to images loaded into the app
        self.loaded_images = []

        # Variables to hold image and drag state
        self.dragging_image = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragged_widget = None

    def load_images(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            try:
                # Clear the third column before loading new images
                for widget in self.column3.winfo_children():
                    widget.destroy()

                # Load images from the selected folder
                image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

                if not image_files:
                    messagebox.showinfo("No Images", "No image files found in the selected folder.")
                    return

                # Store loaded images and display them in column3
                for image_file in image_files:
                    img_path = os.path.join(folder_path, image_file)
                    img = Image.open(img_path)
                    img.thumbnail((150, 150))  # Resize image to fit in the column
                    img_tk = ImageTk.PhotoImage(img)

                    # Add the image to loaded_images list
                    self.loaded_images.append(img_tk)

                    # Create label for each image and display it in column3
                    img_label = tk.Label(self.column3, image=img_tk)
                    img_label.image = img_tk  # Keep a reference to avoid garbage collection
                    img_label.pack(padx=10, pady=5)

                    # Bind mouse events for dragging
                    img_label.bind("<ButtonPress-1>", self.start_drag)
                    img_label.bind("<B1-Motion>", self.do_drag)
                    img_label.bind("<ButtonRelease-1>", self.end_drag)

                # Update scroll region after images are loaded
                self.column_frame.update_idletasks()
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading images: {e}")

    def export_images(self):
        # Placeholder function for export functionality
        pass

    def start_drag(self, event):
        """Start dragging the image widget"""
        self.dragging_image = event.widget
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.dragged_widget = event.widget

        # Bring the image to the front
        self.dragging_image.lift()

        # Move the image outside the column structure to the root window
        self.dragging_image.place_forget()

    def do_drag(self, event):
        """Move the image widget with the mouse"""
        if self.dragging_image:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.dragging_image.place(x=self.dragging_image.winfo_x() + dx, y=self.dragging_image.winfo_y() + dy)

    def end_drag(self, event):
        """Snap the image to the column where it is dropped"""
        if self.dragging_image:
            target_column = None

            # Check if the image is dropped into any of the columns
            for column in [self.column1, self.column2, self.column3]:
                column_bbox = column.bbox("all")
                if column_bbox:
                    column_x1, column_y1, column_x2, column_y2 = column_bbox
                    if column_x1 <= event.x_root <= column_x2 and column_y1 <= event.y_root <= column_y2:
                        target_column = column
                        break

            if target_column:
                # Remove from old position and place in target column
                self.dragging_image.place_forget()
                self.dragging_image.pack(in_=target_column, padx=10, pady=5)
            else:
                # If dropped outside, place back to original column
                self.dragging_image.place_forget()
                self.dragging_image.pack(in_=self.column3, padx=10, pady=5)

            # Ensure the image is on top
            self.dragging_image.lift()

            self.dragging_image = None
            self.dragged_widget = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLoaderApp(root)
    root.mainloop()
