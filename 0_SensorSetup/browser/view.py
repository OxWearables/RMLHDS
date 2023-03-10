from tkinter import *
from tkinter import ttk

from PIL import Image, ImageTk

from constants import *


class View:
    """
    Basic layout of the GUI.
    """

    def __init__(self, root):
        self.root = root

        # content is a 2 row by 2 column grid
        content = ttk.Frame(root)  # create a frame to hold the content
        content.grid(column=0, row=0)  # add to root

        # =================== Schema Frame  =================== (left)
        # create a frame for annotations on the left
        self.schema_holder = ttk.Frame(content, padding=FRAME_PAD)
        self.schema_holder.grid(column=0, row=0, rowspan=2, sticky="ns")
        self.schema_frame = ttk.Frame(
            self.schema_holder,
            padding=SUBFRAME_PAD,
            borderwidth=BORDER_WIDTH,
            relief="solid",
        )
        # add padding to the left and right
        self.schema_frame.grid(column=0, row=0, sticky="n")

        # -> model will update schema frame to show available labels

        # =================== Image Frame =================== (top right)
        # create a frame for images on the right
        self.image_frame = ttk.Frame(content, padding=FRAME_PAD)
        self.image_frame.grid(column=1, row=0)

        # add placeholder text saying Images loading... which will be replaced by images
        self.image_placeholder_text = ttk.Label(
            self.image_frame, text="Images loading..."
        )
        self.image_placeholder_text.grid(column=0, row=0)

        # -> model will update image frame to show images

        # =================== Input Frame =================== (bottom right)
        # create a frame for the annotation input at the bottom
        self.input_frame = ttk.Frame(content, padding=FRAME_PAD)
        self.input_frame.grid(column=1, row=1)

        # ===== Image navigation
        # add frame at top to navigate between images
        self.image_nav_frame = ttk.Frame(self.input_frame, padding=SUBFRAME_PAD)
        self.image_nav_frame.grid(column=0, row=0)
        # add placeholder text saying Loading controls... which will be replaced by buttons
        ttk.Label(self.image_nav_frame, text="Loading controls...").grid(
            column=0, row=0, sticky="we"
        )

        # ===== Current annotations
        # add frame at top to display current annotations
        self.current_annot_frame = ttk.Frame(self.input_frame, padding=SUBFRAME_PAD)
        self.current_annot_frame.grid(column=0, row=1)

        ttk.Label(self.current_annot_frame, text="No annotations").grid(column=0, row=0)

        # -> controller will populate current_annot_frame with buttons of the current annotations

        # ===== Annotation input
        # add frame in middle where annnotations can be added
        self.annot_input_frame = ttk.Frame(self.input_frame, padding=SUBFRAME_PAD)
        self.annot_input_frame.grid(column=0, row=2)

        ttk.Label(self.annot_input_frame, text="Loading controls...").grid(
            column=0, row=0
        )

        # -> controller will populate annotation_input_frame with widgets

        # ===== Comments input
        # add frame at bottow where comments can be added
        self.comment_frame = ttk.Frame(self.input_frame, padding=SUBFRAME_PAD)
        self.comment_frame.grid(column=0, row=3)

        # -> controller will populate annotation_input_frame with widgets

        # in meanwhile have label placeholder saying "Comments:"
        ttk.Label(self.comment_frame, text="Loading space for comments...").grid(
            column=0, row=0
        )
