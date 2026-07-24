import tkinter as tk

from app.gui import PDFToolboxGUI


def main():
    root = tk.Tk()
    PDFToolboxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
