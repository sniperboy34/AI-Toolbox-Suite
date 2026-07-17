import tkinter as tk

from app.gui import ImageToolboxGUI


def main():
    root = tk.Tk()
    ImageToolboxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
