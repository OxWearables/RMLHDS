from tkinter import *
from tkinter import ttk

from constants import *


class Controller:
    """
    Responsible for handling user input and updating the model.
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

        # get frames from view that have to be updated
        self.image_nav_frame = (
            self.view.image_nav_frame
        )  # point to view's image navigation frame
        self.current_annot_frame = (
            self.view.current_annot_frame
        )  # point to view's current annotation frame
        self.annot_input_frame = (
            self.view.annot_input_frame
        )  # point to view's annotation input frame
        self.comment_frame = self.view.comment_frame  # point to view's comment frame

        # set up view.annot_input_frame
        self.init_annot_input_frame()

        # set up view.comment_frame
        self.init_comment_frame()

        # set up view.image_nav_frame
        self.init_image_nav_frame()

    # =================== Image navigation ====================
    def init_image_nav_frame(self):
        """
        Initialises the area where a user can navigate between images.
        This area has a previous button to the left and a next button to the right.
        """
        # clear the frame (gets rid of loading text)
        for widget in self.image_nav_frame.winfo_children():
            widget.destroy()

        # Add a button to the left saying "Previous"
        self.prev_button = ttk.Button(
            self.image_nav_frame, text="Previous", command=self.prev_image
        )
        self.prev_button.grid(column=0, row=0, sticky="w")
        # TODO disable button if there is no previous image - do same for next button

        # Add a button to the right saying "Next"
        self.next_button = ttk.Button(
            self.image_nav_frame, text="Next", command=self.next_image
        )
        self.next_button.grid(column=1, row=0, sticky="e")

    def next_image(self) -> bool:
        """
        Called when the user clicks the next button.
        Firstly, this should initiate a call to the model to save the annotation table to the save path, with the `model.save_annotations` function.
        The, this should make a call to the model to move to the next row of the dataframe (associated with a batch of images).
        If it is possible to move to the next row of the dataframe, then the model will update the images with `model.display_images` function,
        and the controller will update the current annotation frame with `update_current_annot_frame` function.
        """
        self.model.save_annotations()
        if self.model.next_row():
            if not self._image_changed():
                print("Error changing the image")
                return False
            if not self.load_comment():
                print("Error updating the comment")
                return False
        return True

    def prev_image(self) -> bool:
        """
        Called when the user clicks the previous button.
        """
        self.model.save_annotations()
        if self.model.prev_row():
            if not self._image_changed():
                print("Error changing the image")
                return False
            if not self.load_comment():
                print("Error updating the comment")
                return False
        return True

    def _image_changed(self) -> bool:
        """
        Function that is called when the image changes.
        - Model updates the images with `model.display_images` function,
        - Controller updates the current annotation frame display with `update_current_annot_frame` function.
        """
        success = self.model.display_images()
        success = self.update_current_annot_frame() and success
        return success

    # =================== Annotation input ===================
    def init_annot_input_frame(self):
        """
        Initialises the area where the user can add annotations.
        Looks like:
        Add annotation: [combobox] confidence: [entry box] [add button]
        """
        # clear the frame (gets rid of loading text)
        for widget in self.annot_input_frame.winfo_children():
            widget.destroy()

        # Add label to the left saying "Add annotation:"
        ttk.Label(self.annot_input_frame, text="Add annotation:").grid(column=0, row=0)
        # Add a combobox to the right to select the label, TODO combobox with autocomplete
        self.label_combobox = ttk.Combobox(
            self.annot_input_frame, values=self.model.labels
        )
        self.label_combobox.state(["readonly"])  # means can only go with the options
        self.label_combobox.grid(column=1, row=0)
        # Add a label to the right saying "confidence:"
        ttk.Label(self.annot_input_frame, text="confidence:").grid(column=2, row=0)
        # Add entry box to the right accepting a float between 0 and 1
        self.confidence_placeholder = DoubleVar(value=1.0)
        self.confidence_entry = ttk.Entry(
            self.annot_input_frame,
            text=self.confidence_placeholder,  # default value
            # TODO check that value is float: see zip example,
            # check the value when no longer entering text `<FocusOut>`
            # if value is invalid, make it not possible to add annotation
            # this can be done by disabling the add button
        )
        self.confidence_entry.grid(column=3, row=0)
        # Add button to the right to add the annotation

        self.add_button = ttk.Button(
            self.annot_input_frame, text="Add/update", command=self.add_annotation
        )
        self.add_button.grid(column=4, row=0)
        # TODO also bind the enter key add annotation

    def add_annotation(self) -> bool:
        # get the label and confidence from the combobox and entry box
        label = self.label_combobox.get()
        confidence = self.confidence_entry.get()
        # add the annotation to the annotation table
        if not self.model.add_annotation(label, confidence):
            print(
                f"Error adding annotation: '{label}', {confidence}"
            )  # TODO show error message in GUI
            return False

        # update the current annotation frame
        return self.update_current_annot_frame()

    def update_current_annot_frame(self) -> bool:
        """
        Updates the current list of annotations associated with an image based on data from the model.
        Each annotation is a button that can be clicked to remove the annotation.
        """
        for child in self.current_annot_frame.winfo_children():
            child.destroy()

        labels, confidences = self.model.get_nonzero_annotations()
        for i, (label, confidence) in enumerate(zip(labels, confidences)):
            if not self.add_annotation_button(i, label, confidence):
                print(f"Error adding annotation button: '{label}', {confidence}")

        return True

    def add_annotation_button(self, col: int, label: str, confidence: float) -> bool:
        """
        Adds a button to the current annotation frame.
        """
        annot_frame = ttk.Frame(self.current_annot_frame, padding=ELEMENT_PAD)
        annot_frame.grid(column=col, row=0)
        ttk.Label(annot_frame, text=f"{label}: {confidence}").grid(column=0, row=0)
        # TODO make button a small cross image instead of text
        ttk.Button(
            annot_frame,
            text="x",
            width=1,
            command=lambda: self.remove_annotation(label),
        ).grid(column=1, row=0)

        return True

    def remove_annotation(self, label):
        """
        Removes an annotation from the model.
        """
        if not self.model.remove_annotation(label):
            print(f"Error removing annotation: '{label}'")

        self.update_current_annot_frame()

    # =================== Comment Input ===================
    def init_comment_frame(self):
        """
        Creates a text box where the user can enter comments about the current annotations
        """
        # clear the frame (gets rid of loading text)
        for widget in self.comment_frame.winfo_children():
            widget.destroy()

        # Add label to the left saying "Add comment:"
        ttk.Label(self.comment_frame, text="Add comment:").grid(column=0, row=0)
        # Add text box to the right to enter the comment
        self.comment_text = StringVar(value="")
        self.comment_entry = ttk.Entry(
            self.comment_frame,
            textvariable=self.comment_text,
            width=50,
        )
        self.comment_entry.grid(column=1, row=0)
        # whenever the user leaves the comment box, update the model
        self.comment_entry.bind("<FocusOut>", self.update_comment)

    def load_comment(self):
        """
        Loads the saved comment from the model into the comment entry box.
        """
        comment = self.model.get_comment()
        self.comment_text.set(comment)
        return True

    def update_comment(self, event):
        """
        Updates the comment in the model.
        """
        comment = self.comment_text.get()
        if not self.model.set_comment(comment):
            print(f"Error updating comment: '{comment}'")
            return False
        return True
