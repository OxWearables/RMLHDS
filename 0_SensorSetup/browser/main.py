from tkinter import *

from setup import SetUp


def main():
    # GUI setup
    root = Tk()
    root.title("Camera logger annotation tool")
    
    setup = SetUp(root) # initiates the setup window, and eventually the main window

    # lastly, start the mainloop
    root.mainloop()


if __name__ == "__main__":
    main()
