import tkinter as tk
import tkinter.ttk as ttk
from downloader import runDownloader
from RichText import RichText

helv24b = ("Helvetica", "24", "bold")
helv16b = ("Helvetica", "16", "bold")
helv16 = ("Helvetica", "16")
consolas = ("Consolas", "12")

def _label(frame : tk.Frame, text : str, font : tuple = helv16b, width : int = 15, anchor : str = tk.E):
  return tk.Label(master=frame, text=text, width=width, anchor=anchor, font=font, bg="black", fg="white")

def _entry(frame: tk.Frame, text : str, textvariable : tk.StringVar, show : str = ""):
  ttk.Style().configure('pad.TEntry', padding='5 1 1 1')
  return ttk.Entry(master=frame, width=45, font=helv16, text=text, textvariable=textvariable, show=show, style="pad.TEntry") #, bg="black", highlightbackground="#808080", fg="white")

def _loadValues():
  try:
    f = open(".values", "r")
    lines = f.readlines()
    f.close()
    print(lines)
    if len(lines) == 3:
      return lines
    elif len(lines) == 2:
      return [lines[0], lines[1], ""]
    elif len(lines) == 1:
      return [lines[0], "", ""]
    elif len(lines) == 0:
      return ["", "", ""]
    else:
      return lines[:3]
  except:
    return ["", "", ""]
  
def _onClose(values : list[str]):
  try:
    f = open(".values", "w")
    for i in range(2):
      if not values[i].endswith('\n'): 
        values[i] += '\n'
    f.writelines(values)
    f.close()
  except:
    print("Could not save settings!")

def runGui():
  window = tk.Tk()
  window.configure(bg="black", padx=20, pady=15)
  window.title("Canvas Downloader")

  frameIntroText = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCanvasUrl1 = tk.Frame(master=window, borderwidth=1, bg="black")  
  frameCanvasUrl2 = tk.Frame(master=window, borderwidth=1, bg="black")  
  frameCanvasToken1 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameCanvasToken2 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameFilePath1 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameFilePath2 = tk.Frame(master=window, borderwidth=1, bg="black")
  frameDownloadBtn = tk.Frame(master=window, borderwidth=1, bg="black")
  frameDownloadInfo = tk.Frame(master=window, borderwidth=1, bg="black")

  v1, v2, v3 = _loadValues()
  sv1 = tk.StringVar(value=v1.strip())
  sv2 = tk.StringVar(value=v2.strip())
  sv3 = tk.StringVar(value=v3.strip())
  downloadStatus = tk.StringVar(value="Download")

  def callback1(var, index, mode):
    nonlocal v1
    v1 = sv1.get()

  def callback2(var, index, mode):
    nonlocal v2
    v2 = sv2.get()  
    
  def callback3(var, index, mode):
    nonlocal v3
    v3 = sv3.get()

  def downloadBtnClick():
    downloadBtn['state'] = tk.DISABLED
    window.update_idletasks()
    downloadStatus.set("Downloading...")
    window.update_idletasks()
    runDownloader(v3.strip(), v1.strip(), v2.strip(), window, textDownloadInfo)
    downloadStatus.set("Download")
    window.update_idletasks()
    downloadBtn['state'] = tk.NORMAL
    window.update_idletasks()

  labelIntroText = _label(frameIntroText, "Canvas Downloader", helv24b, 25, tk.CENTER)
  labelCanvasUrl = _label(frameCanvasUrl1, "Canvas URL: ")
  entryCanvasUrl = _entry(frameCanvasUrl2, text=v1, textvariable=sv1)
  labelCanvasToken = _label(frameCanvasToken1, text="Canvas Token: ")
  entryCanvasToken = _entry(frameCanvasToken2, text=v2, textvariable=sv2, show="\u2022")
  labelFilePath = _label(frameFilePath1, text="Canvas File Path: ")
  entryFilePath = _entry(frameFilePath2, text=v3, textvariable=sv3)
  downloadBtn = tk.Button(
      master=frameDownloadBtn,
      textvariable=downloadStatus,
      font=helv16, command=downloadBtnClick,
      state=tk.NORMAL,
      bg="#404040",
      highlightbackground="#404040",
      fg="white")
  scrollDownloadInfo = tk.Scrollbar(master=frameDownloadInfo)
  textDownloadInfo = RichText(
    master=frameDownloadInfo,
    bg="black", 
    fg="white", 
    height=20, 
    yscrollcommand=scrollDownloadInfo.set)

  textDownloadInfo.config(font=consolas)
  scrollDownloadInfo.config(command=textDownloadInfo.yview)
  scrollDownloadInfo.pack(side=tk.RIGHT, fill=tk.Y)

  sv1.trace_add("write", callback1)
  sv2.trace_add("write", callback2)
  sv3.trace_add("write", callback3)

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
  entryFilePath.pack_configure(padx=14)
  entryFilePath.pack()
  frameDownloadBtn.grid(row=4, column=0, pady=4, columnspan=2)
  downloadBtn.pack(fill=tk.X)
  frameDownloadInfo.grid(row=5, column=0, pady=4, columnspan=2)
  textDownloadInfo.pack(side=tk.LEFT)

  window.mainloop()

  _onClose([v1, v2, v3])