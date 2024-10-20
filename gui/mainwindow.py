"""Module that runs the primary graphical user interface (GUI) of the Canvas downloader
application.
"""

import threading
import tkinter as tk
import tkinter.ttk as ttk
from downloader import Downloader
from RichText import RichText
from gui.components import entry, Font, label
from gui.coursefilters import CourseFilterWindow

def _loadValues():
  """Loads the values from local storage (`.values` file) when the application is opened (if they exist).
  If values do not exist, the value will be represented as blank for users to enter in the GUI.

  Returns:
    list[str]: A list of [Canvas URL, Canvas API token, Local file save location, Course filters] to be loaded.
  """
  try:
    f = open(".values", "r")
    lines = f.readlines()
    f.close()
    print(lines)
    if len(lines) == 4:
      return lines
    elif len(lines) == 3:
      return [lines[0], lines[1], lines[2], ""]
    elif len(lines) == 2:
      return [lines[0], lines[1], "", ""]
    elif len(lines) == 1:
      return [lines[0], "", "", ""]
    elif len(lines) == 0:
      return ["", "", "", ""]
    else:
      return lines[:4]
  except:
    return ["", "", "", ""]
  
def _onClose(values : list[str]):
  """Handles the saving of values into local storage (`.values` file) when the application is closed.
  This ensures that users do not need to re-enter the Canvas API information as the app will automatically
  populate the values currently in the `.values` file on re-open (in `_loadValues()`).

  Args:
    values (list[str]): A list of [Canvas URL, Canvas API token, Local file save location, Course filters]
  """
  try:
    f = open(".values", "w")
    for i in range(3):
      if not values[i].endswith('\n'): 
        values[i] += '\n'
    f.writelines(values)
    f.close()
  except:
    print("Could not save settings!")

def runGui():
  """Runs the main GUI of the application by rendering a new TKinter window with the necessary form fields.
  """
  window = tk.Tk()
  window.configure(bg="black", padx=20, pady=15)
  window.title("Canvas Downloader")

  # the frame variables ending with 1 represent the frame for the 1st column,
  # 2 represents the frame for the 2nd column.
  frameIntroText = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCanvasUrl1 = tk.Frame(master=window, borderwidth=1, bg="black")  
  frameCanvasUrl2 = tk.Frame(master=window, borderwidth=1, bg="black")  
  frameCanvasToken1 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCanvasToken2 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameFilePath1 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameFilePath2 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCourseFilters1 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCourseFilters2 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameDownloadBtn = tk.Frame(master=window, borderwidth=1)
  frameDownloadInfo = tk.Frame(master=window, borderwidth=1, bg="black")

  # v1 represents the Canvas URL
  # v2 represents the Canvas API token
  # v3 represents the location of the Canvas files on your local machine
  # v4 represents the comma-separated course filters for the Canvas downloader.
  v1, v2, v3, v4 = _loadValues()
  sv4Display = tk.StringVar(value=v4 if v4 != "" else "All courses")
  sv1 = tk.StringVar(value=v1.strip())
  sv2 = tk.StringVar(value=v2.strip())
  sv3 = tk.StringVar(value=v3.strip())
  sv4 = tk.StringVar(value=v4.strip())
  downloadStatus = tk.StringVar(value="Download")

  def callback1(var, index, mode):
    nonlocal v1, downloader
    v1 = sv1.get()
    downloader.canvasUrl = v1

  def callback2(var, index, mode):
    nonlocal v2, downloader
    v2 = sv2.get()  
    downloader.canvasToken = v2
    
  def callback3(var, index, mode):
    nonlocal v3, downloader
    v3 = sv3.get()
    downloader.root = v3
    
  def callback4(var, index, mode):
    nonlocal v4
    v4 = sv4.get()
    sv4Display.set(sv4.get() if sv4.get() != "" else "All courses")
    downloader.filters = v4.strip().split(", ")

  def downloadBtnClick(downloader : Downloader):
    """Handles the click event of the download button (`downloadBtn`).
    """
    downloadBtn['state'] = tk.DISABLED
    window.update_idletasks()
    downloadStatus.set("Downloading...")
    window.update_idletasks()
    def run():
      downloader.run()
      downloadStatus.set("Download")
      window.update_idletasks()
      downloadBtn['state'] = tk.NORMAL
      window.update_idletasks()

    # run the download operation in a separate thread to ensure GUI doesn't freeze
    # during the download process
    threading.Thread(target=run).start()

  labelIntroText = label(frameIntroText, "Canvas Downloader", Font.helv24b, 25, tk.CENTER)
  labelCanvasUrl = label(frameCanvasUrl1, "Canvas URL: ")
  entryCanvasUrl = entry(frameCanvasUrl2, text=v1, textvariable=sv1)
  labelCanvasToken = label(frameCanvasToken1, text="Canvas Token: ")
  entryCanvasToken = entry(frameCanvasToken2, text=v2, textvariable=sv2, show="\u2022")
  labelFilePath = label(frameFilePath1, text="Canvas File Path: ")
  entryFilePath = entry(frameFilePath2, text=v3, textvariable=sv3)
  labelCourseFilters1 = label(frameCourseFilters1, text="Download courses: ")
  labelCourseFilters2 = tk.Message(master=frameCourseFilters2, textvariable=sv4Display, font=Font.helv16, width=395, justify=tk.LEFT, bg="black", fg="white")

  scrollDownloadInfo = tk.Scrollbar(master=frameDownloadInfo)
  textDownloadInfo = RichText(
    master=frameDownloadInfo,
    bg="black", 
    fg="white", 
    height=20, 
    yscrollcommand=scrollDownloadInfo.set)

  scrollDownloadInfo.config(command=textDownloadInfo.yview)
  scrollDownloadInfo.pack(side=tk.RIGHT, fill=tk.Y)
  textDownloadInfo.config(font=Font.consolas)

  downloader = Downloader(v3.strip(), v1.strip(), v2.strip(), v4.strip().split(", "), window, textDownloadInfo)

  courseFiltersWindow = CourseFilterWindow(window, downloader, sv4)
  courseFiltersButton = tk.Button(
      master=frameDownloadBtn,
      text="Update Course Filters...",
      font=Font.helv16, command=courseFiltersWindow.open,
      fg="black",
      state=tk.NORMAL)
  downloadBtn = tk.Button(
      master=frameDownloadBtn,
      textvariable=downloadStatus,
      font=Font.helv16, command=lambda : downloadBtnClick(downloader),
      fg="black",
      state=tk.NORMAL)

  sv1.trace_add("write", callback1)
  sv2.trace_add("write", callback2)
  sv3.trace_add("write", callback3)
  sv4.trace_add("write", callback4)

  frameIntroText.grid(row=0, column=0, padx=3, pady=4, columnspan=2)
  labelIntroText.pack(fill=tk.X)
  frameCanvasUrl1.grid(row=1, column=0, pady=2)
  frameCanvasUrl2.grid(row=1, column=1)
  labelCanvasUrl.pack(side="left")
  entryCanvasUrl.pack()
  frameCanvasToken1.grid(row=2, column=0, pady=2)
  frameCanvasToken2.grid(row=2, column=1)
  labelCanvasToken.pack(side="left")
  entryCanvasToken.pack()
  frameFilePath1.grid(row=3, column=0, pady=2)
  frameFilePath2.grid(row=3, column=1)
  labelFilePath.pack(side="left")
  entryFilePath.pack()
  frameCourseFilters1.grid(row=4, column=0, pady=2)
  frameCourseFilters2.grid(row=4, column=1, sticky="we")
  labelCourseFilters1.pack(side="left", anchor="n")
  labelCourseFilters2.pack(side="left", padx=(10, 0))
  frameDownloadBtn.grid(row=5, column=0, pady=4, columnspan=2)
  courseFiltersButton.pack(side="left")
  downloadBtn.pack(side="left")
  frameDownloadInfo.grid(row=6, column=0, pady=4, columnspan=2)
  textDownloadInfo.pack(side=tk.LEFT)

  window.mainloop()

  _onClose([v1, v2, v3, v4])