"""Module that runs the Course Filters popup window in the Canvas downloader application.
"""

from tkinter import Event, Label, StringVar, Tk, Toplevel
import tkinter as tk
from downloader import Downloader
from gui.components import Font, entry, label

class CourseFilterWindow:

  def __init__(self, master : Tk, downloader : Downloader, contentVar : StringVar):
    self.__isOpen = False
    self.__master = master
    self.__downloader = downloader
    self.__contentVar = contentVar

  def close(self, event : Event = None):
    self.__isOpen = False

  def open(self):

    if not self.__isOpen:

      courseFiltersWindow = Toplevel(self.__master, bg="black")

      courseFiltersWindow.title("Update Course Filters...")
      
      courseFiltersWindow.geometry("640x500")

      mainFrame = tk.Frame(courseFiltersWindow, bg="black")

      listView = tk.Listbox(
        master=mainFrame,
        height=14
      )

      for courseStr in self.__contentVar.get().strip().split(', '):
        listView.insert(tk.END, courseStr)
      
      addContent = ""
      addContentVar = tk.StringVar(value=addContent)

      def updateContent():
        self.__contentVar.set(', '.join(listView.get(0, tk.END)))

      def addContentCallback(var, index, mode):
        nonlocal addContent
        addContent = addContentVar.get()

      addContentVar.trace_add("write", addContentCallback)
      
      def addBtnClick():
        courseList = listView.get(0, tk.END)

        if len(addContent.strip()) > 0 and ',' not in addContent and addContent not in courseList:
          listView.insert(tk.END, addContent)
          updateContent()

          statusVar.set(f"{addContent} added successfully")
          addContentVar.set("")
        elif len(addContent.strip()) > 0 and ',' not in addContent:
          statusVar.set("Could not add as course already exists in the course list!")
        else:
          statusVar.set("Could not add as course contains comma or is empty!")

      def loadCoursesBtnClick():
        courses = self.__downloader.fetchCourses()
        listView.delete(0, tk.END)
        for course in courses:
          listView.insert(tk.END, course.course_code)
        updateContent()

        statusVar.set(f"Courses loaded from Canvas API successfully!")

      def removeBtnClick():
        if listView.curselection():
          selected = listView.curselection()
          removedItem = listView.get(selected)
          listView.delete(selected)
          if selected[0] != listView.index(tk.END):
            listView.selection_set(selected)
          elif listView.index(tk.END) != 0:
            listView.selection_set((selected[0] - 1,))
          else:
            removeBtn['state'] = tk.DISABLED

          statusVar.set(f"{removedItem} removed successfully")

          updateContent()

      def clearBtnClick():
        listView.delete(0, tk.END)
        updateContent()
        removeBtn['state'] = tk.DISABLED

        statusVar.set(f"Courses cleared successfully!")

      def closeBtnClick():
        courseFiltersWindow.destroy()

      addFrame = tk.Frame(mainFrame, bg="black")
      addEntry = entry(frame=addFrame, text=addContent, textvariable=addContentVar)
      addBtn = tk.Button(master=addFrame, text="Add", font=Font.helv16, command=addBtnClick, fg="black", state=tk.NORMAL)
      btnFrame = tk.Frame(mainFrame, bg="black")
      loadCoursesBtn = tk.Button(master=btnFrame, text="Load courses from Canvas API", font=Font.helv16, command=loadCoursesBtnClick, fg="black", state=tk.NORMAL)
      removeBtn = tk.Button(master=btnFrame, text="Remove selected course", font=Font.helv16, command=removeBtnClick, fg="black", state=tk.NORMAL)
      btnFrame2 = tk.Frame(mainFrame, bg="black")
      clearBtn = tk.Button(master=btnFrame2, text="Clear courses", font=Font.helv16, command=clearBtnClick, fg="black", state=tk.NORMAL)
      closeBtn = tk.Button(master=btnFrame2, text="Close Window", font=Font.helv16, command=closeBtnClick, fg="black", state=tk.NORMAL)
      
      statusVar = StringVar(value="Ready")
      sbar = tk.Label(courseFiltersWindow, textvariable=statusVar, bg="black", padx=2, anchor="w")

      def onSelect(event : Event):
        print(listView.curselection())
        if not listView.curselection():
          removeBtn['state'] = tk.DISABLED
        else:
          removeBtn['state'] = tk.NORMAL

      courseFiltersWindow.grid_rowconfigure(0, weight=1)  # Allow row 0 to expand
      courseFiltersWindow.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand
      mainFrame.grid(row=0, column=0, sticky="nsew")

      labelTitle = label(mainFrame, "Courses to Download", Font.helv24b, 25, tk.CENTER)
      labelTitle.grid(row=0, column=0, padx=2, pady=4, sticky="n")

      descMsg = "To load current courses from the Canvas API, click on the 'Load Courses from Canvas API' button. " + \
         "To add a new course, type in the new course code and press the 'Enter' key or click on the 'Add' " + \
         "button. To remove a course, select the course to remove and press the 'Backspace' key or click on the " + \
         "'Remove selected course' button. If empty, all courses will be downloaded. The courses to download are listed below:"
      labelDesc = tk.Message(master=mainFrame, text=descMsg, font=Font.helv12, width=600, bg="black", anchor=tk.CENTER)
      labelDesc.grid(row=1, column=0, padx=12, pady=4, sticky="we")

      listView.grid(row=2, column=0, padx=12, pady=4, sticky="nsew")
      listView.bind('<<ListboxSelect>>', onSelect)

      addFrame.grid(row=3, column=0, padx=4, pady=2)
      addEntry.pack(side=tk.LEFT, padx=4)
      addBtn.pack(side=tk.LEFT, padx=4)
      
      btnFrame.grid(row=4, column=0, padx=4, pady=2)
      loadCoursesBtn.pack(side=tk.LEFT, padx=4)
      removeBtn.pack(side=tk.LEFT, padx=4)
      
      btnFrame2.grid(row=5, column=0, padx=4, pady=4)
      clearBtn.pack(side=tk.LEFT, padx=4)
      closeBtn.pack(side=tk.LEFT, padx=4)

      sbarborder = tk.Frame(courseFiltersWindow, height=2, bg="gray")
      sbarborder.grid(row=1, column=0, sticky="ew")

      sbar.grid(row=2, column=0, sticky="ew", padx=2, pady=(0, 3))
      
      courseFiltersWindow.grid_rowconfigure(2, weight=0)

      addEntry.bind('<Return>', lambda event: addBtnClick())
      listView.bind('<BackSpace>', lambda event : removeBtnClick())
      courseFiltersWindow.bind('<Escape>', lambda event : closeBtnClick())
      courseFiltersWindow.bind('<Destroy>', self.close)

      self.__isOpen = True