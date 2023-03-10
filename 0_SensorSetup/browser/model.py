from tkinter import *
from tkinter import ttk
from tkinter import messagebox


from PIL import Image, ImageTk

from annotation import create_annot_table, load_annot_table, save_annot_table
from constants import *
from image import process_imgs
from schema import parse_schema
from view import View


class Model:
    """
    The model is centered around a pandas dataframe, the `annotation_df` that stores the annotations.
    It contains methods that update and load data from this dataframe.
    It is updated by the contoller (which receives inputs from the user) and it is responsible
    for handling representations of the data in the view which are not interacted with by the user.
    """

    def __init__(
        self,
        img_root_dir: str,
        n_display_images: int,
        image_index: int,  # of the n displayed images, which image to annotate
        schema_path: str,
        save_path: str,
        view: View,
        n_processes: int = 4,
        rotate_image: int = -90,
    ):
        # Class attributes
        self.n_display_images = n_display_images
        self.image_index = image_index  # also how many images to display to the left of the current image
        self.images_to_right = n_display_images - image_index - 1
        self.rotate_image = rotate_image
        self.save_path = save_path
        self.view = view

        # =============== Initialise pandas dataframe: "annotation_df"
        # load images
        img_path_format = img_root_dir + "/P*/*.JPG"
        img_df = process_imgs(img_path_format, n_processes=n_processes)
        # load schema
        self.labels = parse_schema(schema_path)
        # Initialise annotation table
        annotation_df = create_annot_table(img_df, self.labels)
        # sort annotation df by ID, then time
        annotation_df = annotation_df.sort_values(by=["id", "time"])
        self.annotation_df = annotation_df.reset_index(
            drop=True
        )  # reset index to be 0, 1, 2, ...

        # find first valid row
        self.row = image_index - 1
        if not self.next_row():
            messagebox.showinfo(message="No images to display.")
            return None

        # =============== Initialise view
        self.init_schema_frame()  # populates the schema frame with labels
        self.display_images()  # displays the initial images in the image frame

    def init_schema_frame(self):
        """
        Displays the parsed labels in the schema frame as a list of labels
        """
        # add label at the top saying "Annotations:"
        ttk.Label(self.view.schema_frame, text="Annotations:").grid(column=0, row=0)
        # add frame to save labels
        label_frame = ttk.Frame(self.view.schema_frame)
        label_frame.grid(column=0, row=1)
        for i, label in enumerate(self.labels):
            ttk.Label(label_frame, text=label).grid(column=0, row=i)
        # add scrollbar if length of annotations exceeds the height of the screen
        # TODO

    # =============== Changing rows

    def next_row(self):
        """
        Move to next row to annotate.
        Checks that we do not go beyond end of the dataframe,
        and that all images belong to the same participant.
        """
        # Check that we are not at the end of the dataframe
        if self.row == len(self.annotation_df) - self.images_to_right - 1:
            return False

        for next_row in range(
            self.row + 1, len(self.annotation_df) - self.images_to_right
        ):
            if self._check_row_ids(next_row):
                self.row = next_row
                # update View to display next set of images
                return True

        return False

    def prev_row(self):
        """
        Move to previous row to annotate.
        Checks that we do not go beyond beginning of the dataframe,
        and that all images belong to the same participant.
        """
        # Check that we are not at the beginning of the dataframe
        if self.row == self.image_index:
            return False

        for prev_row in range(self.row - 1, self.image_index - 1, -1):
            if self._check_row_ids(prev_row):
                self.row = prev_row
                # update View to display next set of images
                return True

        return False

    def _check_row_ids(self, row):
        """
        Checks that the IDs in range [row - self.image_index, row + self.images_to_right] are the same.
        """
        if (
            not self.annotation_df.loc[
                row - self.image_index : row + self.images_to_right, "id"
            ].nunique()
            == 1
        ):
            return False

        return True

    # =============== Displaying images

    def display_images(self):
        """
        Displays the images in the image frame of the view.
        Images start at the current row and includes self.image_index images to the left and self.images_to_right images to the right.
        Returns true if the images were displayed and false if there are no more images to display.
        """
        if self.row + self.images_to_right >= len(self.annotation_df):
            return False

        # clear the image frame
        for widget in self.view.image_frame.winfo_children():
            widget.destroy()

        # add a loading label while images are being loaded
        self.loading_text = ttk.Label(self.view.image_frame, text="Loading...")
        self.loading_text.grid(column=0, row=0)

        self.images_on_screen = (
            []
        )  # need pointers to current images on display, otherwise they get garbage collected
        # add self.n_display_images frames to the view.image_frame
        for i in range(self.n_display_images):
            img_index = self.row - self.image_index + i
            # add frame
            image_box = ttk.Frame(self.view.image_frame, padding=ELEMENT_PAD)
            if i == self.image_index:
                image_box.config(borderwidth=BORDER_WIDTH, relief="solid")
            image_box.grid(column=i, row=0)

            # read image and timestamp from dataframe
            image = Image.open(self.annotation_df.loc[img_index, "path"])
            image = image.rotate(self.rotate_image, expand=True)
            image = self.resize_image(image)
            img = ImageTk.PhotoImage(image)
            self.images_on_screen.append(img)

            timestamp = self.annotation_df.loc[img_index, "time"]
            # format timestamp to display day and time as day, %d day %Hh%M:%S
            timestamp = timestamp.strftime("Day %d, %Hh%M:%S")

            # add label with timestamp above image, centered
            ttk.Label(image_box, text=timestamp).grid(column=0, row=0)

            ttk.Label(image_box, image=self.images_on_screen[-1]).grid(column=0, row=1)

        # remove loading label
        self.loading_text.destroy()

        return True

    def resize_image(self, image):
        """
        Resize image so that n_display images fit side by side in the image_frame.
        Maintain aspect ratio of the images.
        """
        # get ideal width and height of image frame
        # ideal the image frame should occupy 3/4 of the width of the screen and 3/5 of the height of the screen
        # get size of current display from self.view.root.winfo_width() and self.view.root.winfo_height()
        ideal_image_frame_width = self.view.root.winfo_screenwidth() * 3 // 4
        ideal_image_frame_height = self.view.root.winfo_screenheight() * 3 // 5
        max_width = ideal_image_frame_width // self.n_display_images
        max_height = ideal_image_frame_height
        # calculate size of each image
        resize_ratio = min(max_width / image.width, max_height / image.height)
        image = image.resize(
            (int(image.width * resize_ratio), int(image.height * resize_ratio)),
            Image.ANTIALIAS,
        )

        return image

    # ============== Adding and removing annotations

    def add_annotation(self, label, confidence):
        if label not in self.labels:
            return False
        try:
            confidence = float(confidence)
            if confidence < 0 or confidence > 1:
                return False
        except ValueError:
            return False
        self.annotation_df.loc[self.row, label] = confidence
        return True  # now controller must update view with label buttons

    def remove_annotation(self, label):
        if label not in self.labels:
            return False
        self.annotation_df.loc[self.row, label] = 0
        return True

    def get_nonzero_annotations(self):
        """
        Returns a list of labels that have been annotated
        """
        row_label_data = self.annotation_df.loc[self.row, self.labels]
        non_zero = row_label_data[row_label_data > 1e-5]
        confidences = non_zero.values.tolist()
        labels = non_zero.index.tolist()
        return labels, confidences

    def save_annotations(self) -> bool:
        return save_annot_table(self.annotation_df, self.save_path)

    # TODO, understand under which circumstances reloading is needed

    # ================= Comment getters and setters
    def get_comment(self) -> str:
        return self.annotation_df.loc[self.row, "comment"]

    def set_comment(self, comment: str) -> bool:
        self.annotation_df.loc[self.row, "comment"] = comment
        return True
