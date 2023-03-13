from tkinter import *
from tkinter import messagebox, ttk

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
        rotate_image: int = 0,
    ):
        # Class attributes
        self.n_display_images = n_display_images
        self.image_index = image_index  # also how many images to display to the left of the current image
        self.images_to_right = n_display_images - image_index - 1
        self.rotate_image = rotate_image
        self.save_path = save_path
        self.view = view

        # image related
        self.loading_text = None
        self.images_on_screen = None

        # =============== Initialise pandas dataframe: "annotation_df"
        # load images
        img_path_format = img_root_dir + "/P*/*.JPG"
        img_df = process_imgs(img_path_format, n_processes=n_processes)

        # check there are images to display
        if len(img_df) == 0:
            messagebox.showinfo(message="No images to display.")
            return None

        # load schema
        self.labels = parse_schema(schema_path)
        # Initialise annotation table
        annotation_df = create_annot_table(img_df, self.labels)
        # sort annotation df by ID, then time
        annotation_df = annotation_df.sort_values(by=["id", "time"])
        self.annotation_df = annotation_df.reset_index(
            drop=True
        )  # reset index to be 0, 1, 2, ...

        # =============== Initialise row
        self.row = 0  # current row to annotate
        self.n_participant_photos = (
            self.count_participant_photos()
        )  # count number of photos for current participant
        self.participant_start_row = (
            self.row
        )  # row where the current participant starts

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
        Checks that we do not go beyond end of the dataframe
        """
        # Check that we are not at the end of the dataframe
        if self.row == len(self.annotation_df) - 1:
            return False

        self.row += 1
        # if we switch to a new participant, reset the participant start row, and recalculate the number of photos for the participant
        if (
            self.annotation_df.loc[self.row, "id"]
            != self.annotation_df.loc[self.row - 1, "id"]
        ):
            self.participant_start_row = self.row
            self.n_participant_photos = self.count_participant_photos()

        return True

    def prev_row(self) -> bool:
        """
        Move to previous row to annotate.
        Checks that we do not go beyond beginning of the dataframe.
        """
        # Check that we are not at the beginning of the dataframe
        if self.row == 0:
            return False

        self.row -= 1
        # if we switch to a new participant, reset the participant start row, and recalculate the number of photos for the participant
        if (
            self.annotation_df.loc[self.row, "id"]
            != self.annotation_df.loc[self.row + 1, "id"]
        ):
            self.n_participant_photos = self.count_participant_photos()
            self.participant_start_row = self.row - self.n_participant_photos + 1

        return True

    def count_participant_photos(self) -> int:
        """
        Counts the number of photos for the current participant.
        """
        return len(
            self.annotation_df[
                self.annotation_df.id == self.annotation_df.loc[self.row, "id"]
            ]
        )

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
        Displays the images in the image frame of the view, the particpant ID, and how many images have been annotated so far.
        Makes a call to the adapt_image_display to get:
        - How many images to display: n_display_images,
        - Which image to draw a bounding box around: image_index,
        Returns true if the images were displayed and false if there are no more images to display.
        """
        n_display_images, image_index, images_to_right = self.adapt_image_display()

        if self.row + images_to_right >= len(self.annotation_df):
            return False
        if self.row - image_index < 0:
            return False

        # add text to information_frame on which image we are currently on
        for widget in self.view.information_frame.winfo_children():
            widget.destroy()

        ttk.Label(
            self.view.information_frame,
            text=f"Image {self.row + 1} of {len(self.annotation_df)}",
        ).grid(column=0, row=0)

        # clear the image frame
        for widget in self.view.image_frame.winfo_children():
            widget.destroy()

        # add particant ID to the top of the image frame
        ttk.Label(
            self.view.image_frame,
            text=f"Participant: {self.annotation_df.loc[self.row, 'id']}",
        ).grid(column=0, row=0, columnspan=self.n_display_images)

        # add a loading label while images are being loaded
        self.loading_text = ttk.Label(self.view.image_frame, text="Loading...")
        self.loading_text.grid(column=0, row=1, columnspan=self.n_display_images)

        self.images_on_screen = (
            []
        )  # need pointers to current images on display, otherwise they get garbage collected
        # add self.n_display_images frames to the view.image_frame
        for i in range(n_display_images):
            img_index = self.row - image_index + i
            # add frame
            image_box = ttk.Frame(self.view.image_frame, padding=ELEMENT_PAD)
            if i == image_index:
                image_box.config(borderwidth=IMG_BORDER_WIDTH, relief="solid")
            image_box.grid(column=i, row=1)

            # read image and timestamp from dataframe
            image = Image.open(self.annotation_df.loc[img_index, "path"])
            image = image.rotate(self.rotate_image, expand=True)
            image = self.resize_image(image)
            img = ImageTk.PhotoImage(image)
            self.images_on_screen.append(img)

            timestamp = self.annotation_df.loc[img_index, "time"]
            # format timestamp to display date and time as yyyy/mm/dd HHhMM:SS
            timestamp = timestamp.strftime("%Y/%m/%d %Hh%M:%S")

            # add label with timestamp above image, centered
            ttk.Label(image_box, text=timestamp).grid(column=0, row=0)

            ttk.Label(image_box, image=self.images_on_screen[-1]).grid(column=0, row=1)

        # remove loading label
        self.loading_text.destroy()

        return True

    def adapt_image_display(self):
        """
        Firstly, check if self.n_display_images can be displayed - sometime participants will have less images than self.n_display_images
        Sometimes, self.row is less than self.image_index.
        This happens:
        - if we are near the beginning of the dataframe
        - if we are near the end of the dataframe
        - if we are nearing the end of a participant's images
        In this case, we want to move the image index along and keep the same images on screen.
        So, as we increment the row, we temporarily increment the image index, the images to left and decrease the images to right.
        We do the reverse when decrementing the row.

        Returns:
        - n_display_images: the number of images to display
        - image_index: the index of the image within the n_display_images images to draw a bounding box around
        - images_to_right: the number of images to the right of the image_index image (could just be calculated from n_display_images and image_index)
        """
        n_display_images = self.n_display_images
        image_index = self.image_index
        images_to_right = self.images_to_right

        # check if the current participant has enough images to display self.n_display_images images
        # in this case, we display all the images for the participant and just move the image index along
        if self.n_participant_photos <= self.n_display_images:
            n_display_images = self.n_participant_photos
            image_index = self.row - self.participant_start_row
            images_to_right = self.n_participant_photos - image_index - 1
            return n_display_images, image_index, images_to_right

        # now we are sure that the participant has enough images to display self.n_display_images images
        # we just need to check whether we are near the beginning, the end, or near the beginning or end of a participant's images

        # case: near the beginning of the dataframe
        if self.row < self.image_index:
            image_index = self.row
            images_to_right = self.n_display_images - image_index - 1
            return n_display_images, image_index, images_to_right

        # case: near the end of the dataframe
        if self.row + self.images_to_right >= len(self.annotation_df):
            images_to_right = len(self.annotation_df) - self.row - 1
            image_index = self.n_display_images - images_to_right - 1
            return n_display_images, image_index, images_to_right

        # case: nearing the beginning of a participant's images
        if self.row - self.participant_start_row < self.image_index:
            image_index = self.row - self.participant_start_row
            images_to_right = self.n_display_images - image_index - 1
            return n_display_images, image_index, images_to_right

        # case: nearing the end of a participant's images
        if (
            self.row + self.images_to_right - self.participant_start_row
            >= self.n_participant_photos
        ):
            images_to_right = (
                self.n_participant_photos - self.row - self.participant_start_row - 1
            )
            image_index = self.n_display_images - images_to_right - 1
            return n_display_images, image_index, images_to_right

        # finally, case where we are neither at the beginning or end of the dataframe, nor nearing the beginning or end of a participant's images
        return n_display_images, image_index, images_to_right

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
