import tkinter as tk
from tkinter import font as tkFont

class RichText(tk.Text):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    bold_font = ("Consolas", "12", "bold")

    self.tag_configure("bold", font=bold_font)