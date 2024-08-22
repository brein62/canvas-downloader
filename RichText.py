import tkinter as tk
from tkinter import font as tkFont

class RichText(tk.Text):
  """A custom rich text widget with certain customisation options."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # bold and underline settings
    bold_font = ("Consolas", "12", "bold")
    underline_font = ("Consolas", "12", "underline")
    boldunderline_font = ("Consolas", "12", "bold", "underline")

    # tag configuration for specific styles
    self.tag_configure("bold", font=bold_font)
    self.tag_configure("underline", font=underline_font)
    self.tag_configure("boldunderline", font=boldunderline_font)
    self.tag_configure("red", foreground="red")
    self.tag_configure("yellow", foreground="yellow")
    self.tag_configure("green", foreground="green")