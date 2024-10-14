"""Reusable TKinter GUI components for this application."""

import tkinter.ttk as ttk
import tkinter as tk

class Font:
  """Font constants for this application.
  """
  helv24b = ("Helvetica", "24", "bold")
  helv16b = ("Helvetica", "16", "bold")
  helv16 = ("Helvetica", "16")
  helv12 = ("Helvetica", "12")
  consolas = ("Consolas", "12")

def label(frame : tk.Frame, text : str, font : tuple = Font.helv16b, width : int = 18, anchor : str = tk.E, *args, **kwargs) -> tk.Label:
  """Creates the customised label to be used in the GUI.

  Args:
    frame (tk.Frame): The master/parent frame this `ttk.Entry` widget will be located in.
    text (str): The content of the label.
    font (tuple, optional): The font to be used for the label. Defaults to helv16b.
    width (int, optional): The width of the label. Defaults to 18.
    anchor (str, optional): Where to anchor the label in the GUI. Defaults to tk.E.

  Returns:
    tk.Label: The customised label to be used in the GUI.
  """
  return tk.Label(master=frame, text=text, width=width, anchor=anchor, font=font, bg="black", fg="white", *args, **kwargs)

def entry(frame: tk.Frame, text : str, textvariable : tk.StringVar, show : str = "") -> ttk.Entry:
  """Creates the customised TKinter `ttk.Entry` widget (text box) to be used in the GUI.

  Args:
    frame (tk.Frame): The master/parent frame this `ttk.Entry` widget will be located in.

    text (str): The initial content of the text box.

    textvariable (tk.StringVar): The `tk.StringVar` instance to store the content of the text box into,
    to be used within the application.

    show (str, optional): The character to show in place of the individual characters. This can be used
    to create password inputs by setting `show` to `\\u2022` (a centred dot). Defaults to "".

  Returns:
    Entry: The `ttk.Entry` text box instance created by the application.
  """
  ttk.Style().theme_use('clam')
  ttk.Style().configure('pad.TEntry', padding='5 1 1 1', fieldbackground="#d0d0d0", background="#d0d0d0", foreground="black")
  return ttk.Entry(
    master=frame, 
    width=45, 
    font=Font.helv16,
    text=text, 
    textvariable=textvariable, 
    show=show, 
    style="pad.TEntry") #, bg="black", highlightbackground="#808080", fg="white")