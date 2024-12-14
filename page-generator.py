import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

def create_html_file(filename):
    filename = "s:/Software/Github/framedbynick/" + filename
    html_content = """<!DOCTYPE html>
<html>

<head>
    <meta charset=\"utf-8\">
    <link rel=\"stylesheet\"
          href=\"https://fonts.googleapis.com/css?family=Special+Elite\">
    <link rel=\"stylesheet\" href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css\">
    <style>
      body {
        font-family: 'Special Elite', serif;
        font-size: 48px;
      }
    </style>

    <!-- Add stylesheets here -->
    <link rel=\"stylesheet\" href=\"style.css\">
    <link rel=\"stylesheet\" href=\"gallery.css\">

</head>

<body>
    <div class=\"faux-borders\">

        <div class=\"content\">
            <a class=\"lightbox\" href=\"/\">
                <h1>
                    framed by Nick 
                </h1>
            </a>
            <h2>
                title-here
            </h2>
        </div>

"""

    # Write the HTML content to the specified file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

def append_line_to_file(filename, line):
    filename = "s:/Software/Github/framedbynick/" + filename
    """
    Appends a given line to the specified file.

    Parameters:
        filename (str): The path to the file to which the line should be appended.
        line (str): The line of text to append to the file.
    """
    try:
        with open(filename, "a") as file:
            file.write(line + "\n")
    except Exception as e:
        print(f"An error occurred while appending to the file: {e}")


def complete_html(filename):
    filename = "s:/Software/Github/framedbynick/" + filename
    """
    Appends the closing HTML tags to the specified file.

    Args:
        filename (str): The name of the file to append the HTML to.
    """
    closing_lines = [
        "",  # Empty line for spacing
        "    </div>",
        "</body>",
        "",  # Empty line for spacing
        "</html>"
    ]

    with open(filename, 'a') as file:
        for line in closing_lines:
            file.write(line + '\n')


class ImageLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Loader")
        self.root.geometry("1940x1080+0+0")

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

        # Create the context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Hero", command=self.hero_image)
        self.context_menu.add_command(label="Un-Hero", command=self.unhero_image)

        self.current_image_id = None  # Track the image being right-clicked

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
                'y': y_offset,
                'width': img_tk.width(),
                'height': img_tk.height()
            })

            # Store the image reference to prevent garbage collection
            self.image_references.append(img_tk)

            # Bind drag and drop events to the image
            self.make_image_draggable(img_id)

            # Bind right-click event to show context menu
            self.main_pane.tag_bind(img_id, "<Button-3>", self.show_context_menu)

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
        left_images = ['row']
        right_images = ['row']
        export_image_columns = []

        # Sort the images in each section by their y value in descending order
        sorted_images = sorted(self.images, key=lambda img: img['y'], reverse=False)

        # Separate the images into left, right, and hero sections based on their x values
        for img in sorted_images:
            if (img['x']) < 480 and (img['x'] + img['width']) >= 480:
                # Hero Image
                export_image_columns.append(list(left_images))
                export_image_columns.append(list(right_images))
                export_image_columns.append(['hero',img])
                left_images = ['row']
                right_images = ['row']
            elif (img['x'] + img['width']) < 480:
                # Left Column
                left_images.append(img)
            elif (img['x'] + img['width']) >= 480 and (img['x'] + img['width']) < 960:
                # Right Column
                right_images.append(img)
        if (len(left_images)>0):
            export_image_columns.append(list(left_images))
        if (len(right_images)>0):
            export_image_columns.append(list(right_images))

        create_html_file("new-gallery")

        for column_list in export_image_columns:
            print(f"~~~~~~{column_list[0]}~~~~~~")
            if column_list[0] == "hero":
                append_line_to_file("new-gallery", "")
                append_line_to_file("new-gallery", "        <div class=\"hero\">")
            else:
                append_line_to_file("new-gallery", "")
                append_line_to_file("new-gallery", "        <div class=\"row\">")

            for item in column_list[1:]:
                index = item['filename'].find("img")
                if index != -1:
                    filename = item['filename'][index:]
                print(filename)
                if column_list[0] == "hero":
                    append_line_to_file("new-gallery", f"            <a class=\"lightbox\" href=\"{filename}\">")
                    append_line_to_file("new-gallery", f"                <img src=\"{filename}\" loading=\"lazy\">")
                    append_line_to_file("new-gallery", "            </a>")
                else:
                    append_line_to_file("new-gallery", f"            <div class=\"column-double\">")
                    append_line_to_file("new-gallery", f"                <a class=\"lightbox\" href=\"{filename}\">")
                    append_line_to_file("new-gallery", f"                    <img src=\"{filename}\" loading=\"lazy\">")
                    append_line_to_file("new-gallery", "                </a>")
                    append_line_to_file("new-gallery", "            </div>")

            append_line_to_file("new-gallery", "        </div>")

        complete_html("new-gallery")

    def hero_image(self):
        if self.current_image_id:
            for img in self.images:
                if img['id'] == self.current_image_id:
                    # Double the size of the image
                    img['width'] *= 2
                    img['height'] *= 2
                    img_resized = Image.open(img['filename']).resize((img['width'], img['height']))
                    img_resized_tk = ImageTk.PhotoImage(img_resized)
                    self.main_pane.itemconfig(img['id'], image=img_resized_tk)
                    img['image'] = img_resized_tk  # Update the reference
                    self.image_references.append(img_resized_tk)
                    break

    def unhero_image(self):
        if self.current_image_id:
            for img in self.images:
                if img['id'] == self.current_image_id:
                    # Halve the size of the image
                    img['width'] //= 2
                    img['height'] //= 2
                    img_resized = Image.open(img['filename']).resize((img['width'], img['height']))
                    img_resized_tk = ImageTk.PhotoImage(img_resized)
                    self.main_pane.itemconfig(img['id'], image=img_resized_tk)
                    img['image'] = img_resized_tk  # Update the reference
                    self.image_references.append(img_resized_tk)
                    break

    def show_context_menu(self, event):
        # Find the image being right-clicked
        scroll_y = self.main_pane.yview()[0] * self.main_pane.bbox("all")[3]
        adjusted_y = event.y + scroll_y
        self.current_image_id = self.main_pane.find_closest(event.x, adjusted_y)[0]
        self.context_menu.post(event.x_root, event.y_root)


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
