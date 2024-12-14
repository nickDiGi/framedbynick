import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Grid Organizer")

        self.image_folder = None
        self.images = []
        self.image_widgets = []
        self.grid_data = [[], []]  # Two columns

        self.dragged_widget = None
        self.dragged_widget_original_row_col = None

        self.setup_ui()

    def setup_ui(self):
        # Buttons
        self.load_button = tk.Button(self.root, text="Load Images", command=self.load_images)
        self.load_button.pack(pady=10)

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        self.save_button = tk.Button(self.root, text="Export Lists", command=self.export_lists)
        self.save_button.pack(pady=10)

    def load_images(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if not folder:
            return

        self.image_folder = folder
        self.images = []

        # Load images from folder
        for filename in os.listdir(folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                self.images.append(os.path.join(folder, filename))

        if not self.images:
            messagebox.showerror("Error", "No images found in the selected folder.")
            return

        self.display_images()

    def display_images(self):
        # Clear previous widgets and grid data
        for widget in self.image_widgets:
            widget.destroy()
        self.image_widgets = []
        self.grid_data = [[], []]

        for i, image_path in enumerate(self.images):
            col = i % 2  # Alternate between columns
            img = Image.open(image_path)
            img.thumbnail((100, 100))  # Resize image to thumbnail size
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(self.grid_frame, image=img_tk, borderwidth=2, relief="groove")
            label.image = img_tk  # Keep reference to avoid garbage collection
            label.image_path = image_path  # Store image path in label

            label.bind("<ButtonPress-1>", self.start_drag)
            label.bind("<B1-Motion>", self.drag)
            label.bind("<ButtonRelease-1>", self.drop)

            label.grid(row=len(self.grid_data[col]), column=col, padx=5, pady=5)
            self.grid_data[col].append(image_path)
            self.image_widgets.append(label)

    def start_drag(self, event):
        widget = event.widget
        self.dragged_widget = widget

        # Store the original grid position
        for row in range(len(self.grid_data)):
            for col in range(2):
                if widget.image_path in self.grid_data[col]:
                    self.dragged_widget_original_row_col = (row, col)
                    return

    def drag(self, event):
        if self.dragged_widget:
            self.dragged_widget.lift()
            self.dragged_widget.place(x=event.x_root - self.grid_frame.winfo_rootx(),
                                      y=event.y_root - self.grid_frame.winfo_rooty())

    def drop(self, event):
        if not self.dragged_widget:
            return

        x, y = event.widget.winfo_pointerxy()
        target = self.grid_frame.winfo_containing(x, y)

        if target and isinstance(target, tk.Label):
            self.swap_images(self.dragged_widget, target)
        else:
            # Return to original position if dropped in invalid area
            self.dragged_widget.place_forget()
            row, col = self.dragged_widget_original_row_col
            self.dragged_widget.grid(row=row, column=col)

        self.dragged_widget = None

    def swap_images(self, widget1, widget2):
        path1, path2 = widget1.image_path, widget2.image_path

        # Find their positions in grid_data
        for col in range(2):
            if path1 in self.grid_data[col] and path2 in self.grid_data[col]:
                index1, index2 = self.grid_data[col].index(path1), self.grid_data[col].index(path2)
                self.grid_data[col][index1], self.grid_data[col][index2] = path2, path1
                break
            elif path1 in self.grid_data[col]:
                index1 = self.grid_data[col].index(path1)
                other_col = 1 - col
                index2 = self.grid_data[other_col].index(path2)
                self.grid_data[col][index1], self.grid_data[other_col][index2] = path2, path1
                break

        # Refresh the grid display after swapping
        self.display_images()

    def export_lists(self):
        if not any(self.grid_data):
            messagebox.showerror("Error", "No images to export.")
            return

        output = "Column 1:\n" + "\n".join(self.grid_data[0]) + "\n\nColumn 2:\n" + "\n".join(self.grid_data[1])
        messagebox.showinfo("Exported Lists", output)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGridApp(root)
    root.mainloop()
