from tkinterdnd2 import TkinterDnD

from app.gui import ImageToolboxGUI


def main():
    root = TkinterDnD.Tk()
    ImageToolboxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
