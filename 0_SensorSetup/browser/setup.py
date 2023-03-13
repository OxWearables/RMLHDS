from tkinter import *
from tkinter import filedialog, messagebox, ttk

from constants import *
from controller import Controller
from image import check_img_root_dir
from model import Model
from view import View


class SetUp:
    """ "
    When the application starts, open up a window to get the
    - path to the images,
    - path to the schema,
    - path to save the annotations,
    - number (N) of images to display,
    - which image out of the N images to annotate.
    """

    def __init__(self, root):
        self.root = root

        # what needs to get set up:
        self.img_root_dir = None
        self.schema_path = None
        self.save_path = None
        self.n_display_images = None
        self.image_index = None

        # following set up, these get initialised
        self.view = None
        self.model = None
        self.controller = None

        # start new window at front to get paths
        self.window = Toplevel(self.root, padx=FRAME_PAD, pady=FRAME_PAD)
        self.window.title("Set up")

        # ======== Image related:

        # image path
        ttk.Label(self.window, text="Path to image folders:").grid(row=0, column=0)
        # frame to hold the image path and the button to choose the path
        self.image_path_frame = ttk.Frame(self.window)
        self.image_path_frame.grid(row=0, column=1, sticky="e")
        # add empty label to hold the image path
        self.image_path_label = ttk.Label(self.image_path_frame, text="")
        self.image_path_label.grid(row=0, column=0)
        Button(
            self.image_path_frame, text="Choose", command=self.choose_image_path
        ).grid(row=0, column=1, sticky="e")

        # number (N) of images to display
        ttk.Label(self.window, text="Number (N) of images to display:").grid(
            row=1, column=0
        )
        # add combo box to choose between 1 to 5 images
        self.n_display_image_box = ttk.Combobox(self.window, values=[1, 2, 3, 4, 5])
        self.n_display_image_box.state(["readonly"])
        self.n_display_image_box.grid(row=1, column=1)

        # which of the N images to annotate
        ttk.Label(self.window, text="Which of the N images will you annotate?").grid(
            row=2, column=0
        )
        # add combo box to choose between 1 to 5 images
        self.image_index_box = ttk.Combobox(self.window, values=[0, 1, 2, 3, 4])
        self.image_index_box.state(["readonly"])
        self.image_index_box.grid(row=2, column=1)

        # ======== Schema related:
        # schema path
        ttk.Label(self.window, text="Path to annotation schema:").grid(row=3, column=0)
        # frame to hold the schema path and the button to choose the path
        self.schema_path_frame = ttk.Frame(self.window)
        self.schema_path_frame.grid(row=3, column=1, sticky="e")
        # add empty label to hold the schema path
        self.schema_path_label = ttk.Label(self.schema_path_frame, text="")
        self.schema_path_label.grid(row=0, column=0)
        Button(
            self.schema_path_frame, text="Choose", command=self.choose_schema_path
        ).grid(row=0, column=1, sticky="e")

        # ======== Saving (and eventually reloading) related:
        # save path
        ttk.Label(self.window, text="Path to save annotations:").grid(row=4, column=0)
        # frame to hold the save path and the button to choose the path
        self.save_path_frame = ttk.Frame(self.window)
        self.save_path_frame.grid(row=4, column=1, sticky="e")
        # add empty label to hold the save path
        self.save_path_label = ttk.Label(self.save_path_frame, text="")
        self.save_path_label.grid(row=0, column=0)
        Button(self.save_path_frame, text="Choose", command=self.choose_save_path).grid(
            row=0, column=1, sticky="e"
        )

        # ======== Buttons to start the application:
        self.start_button_frame = ttk.Frame(self.window, padding=SUBFRAME_PAD)
        self.start_button_frame.grid(row=5, column=1, sticky="e")
        Button(
            self.start_button_frame, text="Start", command=self.get_selection_and_start
        ).grid(row=5, column=0, sticky="e")

    def choose_image_path(self):
        self.img_root_dir = filedialog.askdirectory(mustexist=True)
        self.image_path_label.config(text=shorten_filepath(self.img_root_dir))

    def choose_schema_path(self):
        self.schema_path = filedialog.askopenfilename()
        self.schema_path_label.config(text=shorten_filepath(self.schema_path))

    def choose_save_path(self):
        self.save_path = filedialog.asksaveasfilename()
        self.save_path_label.config(text=shorten_filepath(self.save_path))

    def get_selection_and_start(self):
        """
        Makes sure there are values for
        - image_path_fomart
        - schema_path
        - save_path
        - n_display_images
        - image_index
        Then it starts the application!
        """
        if self.img_root_dir is None:
            messagebox.showinfo(message="Please choose a path to the images")
            return False
        if self.schema_path is None:
            messagebox.showinfo(message="Please choose a path to the schema")
            return False
        if self.save_path is None:
            messagebox.showinfo(message="Please choose a path to save the annotations")
            return False
        if self.n_display_image_box.get() == "":
            messagebox.showinfo(message="Please choose a number of images to display")
            return False
        if self.image_index_box.get() == "":
            messagebox.showinfo(message="Please choose an image to annotate")
            return False

        self.n_display_images = int(self.n_display_image_box.get())
        self.image_index = int(self.image_index_box.get())

        # check image index is less than n_display_images
        if self.image_index >= self.n_display_images:
            messagebox.showinfo(
                message="Please choose an image index less than the number of images to display"
            )
            return False

        # check that the image directory conforms to the format
        if not check_img_root_dir(self.img_root_dir):
            messagebox.showinfo(
                message="Current image folder is either empty, or is incorrectly formated."
            )
            return False

        # check that the schema is a valid format
        # TODO

        # close the window and start the application
        self.window.destroy()

        self.view = View(self.root)
        self.model = Model(
            self.img_root_dir,
            self.n_display_images,
            self.image_index,
            self.schema_path,
            self.save_path,
            self.view,
            n_processes=4,
        )
        self.controller = Controller(self.model, self.view)
        return True


def shorten_filepath(filepath: str, n_chars=20) -> str:
    """
    Returns the last n_chars of a filepath.
    """
    length = min(len(filepath), n_chars)
    return "..." + filepath[-length:]
