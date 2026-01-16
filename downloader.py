"""A module that encapsulates the Canvas file downloader capability.
"""

import requests
import pathlib
import tkinter as tk
import os

from richtext import RichText
from filemodels import Course, File, FileLog, Folder

os.system("")

class color:
  """The colour constants to be used for this application."""
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'

class Downloader:
  """A class representing a Canvas file downloader."""

  def __init__(self, root : str, canvasUrl : str, canvasToken : str, filters : list[str], displayWindow : tk.Tk = None, displayArea : RichText = None):
    """Creates a Canvas file downloader object.

    Args:
      root (str): The root directory to save the files downloaded into.
      canvasUrl (str): The Canvas URL to access the API using.
      canvasToken (str): The Canvas Token used to access the Canvas API.
      filters (list[str]): The list of course codes to download. If left empty, downloads all courses.
      displayWindow (tk.Tk, optional): The display window for the GUI. Defaults to None.
      displayArea (RichText, optional): The display text area GUI to display the download status onto. Defaults to None.
    """
    self.root = root
    self.canvasUrl = canvasUrl
    self.canvasToken = canvasToken
    self.filters = filters
    self.displayWindow = displayWindow
    self.displayArea = displayArea

  def _isFilterEmpty(self):
    """Checks whether the course filters are left blank. If so, all courses should be downloaded.

    Returns:
      bool: True if course filters are blank, False otherwise.
    """

    # remove all filters that are whitespace
    processedFilters = list(filter(lambda x : x.strip() != '', self.filters))

    return (len(processedFilters) == 0)

  def _print(self, content : str = ""):
    """Prints a status line regarding the Canvas file download process in the console as well as in the
    textarea within the GUI. Converts the console colours/formatting to print properly in the textarea
    based on the specific settings in `RichText`.

    Args:
      content (str, optional): The content to be displayed. Defaults to "".
    """
    print(content)
    if self.displayWindow != None and self.displayArea != None:
      if content.startswith(color.BOLD + color.UNDERLINE) or content.startswith(color.UNDERLINE + color.BOLD):
        self.displayArea.insert(tk.END, content[8:-4] + "\n", "boldunderline")
      elif content.startswith(color.BOLD + color.GREEN) or content.startswith(color.GREEN + color.BOLD):
        self.displayArea.insert(tk.END, content[9:-4] + "\n", ["bold", "green"])
      elif content.startswith(color.BOLD):
        self.displayArea.insert(tk.END, content[4:-4] + "\n", "bold")
      elif content.startswith(color.UNDERLINE):
        self.displayArea.insert(tk.END, content[4:-4] + "\n", "underline")
      elif content.startswith(color.RED):
        self.displayArea.insert(tk.END, content[5:-4] + "\n", "red")
      elif content.startswith(color.YELLOW):
        self.displayArea.insert(tk.END, content[5:-4] + "\n", "yellow")
      elif content.startswith(color.GREEN):
        self.displayArea.insert(tk.END, content[5:-4] + "\n", "green")
      else:
        self.displayArea.insert(tk.END, content + "\n")
      self.displayArea.see("end")
      self.displayWindow.update_idletasks()

  def loadFiles(self) -> list[Course]:
    """Gets the courses and files and organises the files to download as a list of Course
    objects loaded with all the folders and files to download.

    Returns:
      list[Course]: The list of courses, containing folder and file objects that can be
      processed for download.
    """
    self._print(color.UNDERLINE + color.BOLD + f"Retrieving files from courses:" + color.END)
    self._print()
    courseListWithFiles : list[Course] = []
    for course in self.fetchCourses():
      if course.course_code in self.filters or self._isFilterEmpty():
        self._print(color.BOLD + f"Course: {course.name} ({course.course_code})" + color.END)
        foldersArray : list[Folder] = []
        for folder in self.getCourseFolders(course.id):
          courseFolderName = folder.getPath()
          filesInFolder = self.getFilesFromFolder(folder.id)
          self._print(f"{folder.id} {courseFolderName}")
          foldersArray.append(folder.withFiles(filesInFolder))
        self._print()
        courseListWithFiles.append(course.withFolders(foldersArray))
    return courseListWithFiles

  def fetchCanvasAPI(self, apiPath : str) -> requests.Response:
    """Sends a `GET` request to a path within the Canvas API given the Canvas token, and returns
    the response received from the Canvas API.

    Args:
      apiPath (str): The API path within the Canvas API.

    Returns:
      requests.Response: The response received from the Canvas API request made.
    """
    response = requests.get(
      f"{self.canvasUrl}/api/v1/{apiPath}?per_page=1000&access_token={self.canvasToken}",
      headers={
        'Accept': 'application/json'
      }    
    )
    return response

  def fetchCourses(self) -> list[Course]:
    """Fetches the user's courses as a JSON list.

    Returns:
      list: The list of courses by the user, in JSON format.
    """
    try:
      response = self.fetchCanvasAPI('courses')
      if response.status_code == 200:
        text = response.json()
        return Course.fromApiArray(list(filter(lambda course : 'name' in course.keys() and course['name'] != None, text)))
      else:
        self._print(f"Could not fetch courses! HTTP status: {response.status_code}")
        return []
    except Exception as e:
      self._print("Failed to fetch! " + str(e))
      return []
    
  def getCourseFolders(self, courseId : int) -> list[Folder]:
    """Fetches the folders in a course's files given the course ID.

    Args:
      courseId (int): The course ID to fetch the folders from.

    Returns:
      list: The list of folders in the specific course's files, in JSON format.
    """
    try:
      response = self.fetchCanvasAPI(f'courses/{courseId}/folders')
      if response.status_code == 200:
        text = response.json()
        return Folder.fromApiArray(list(text))
      else:
        self._print(f"{color.RED}Could not fetch folders from course ID {courseId}{color.END}")
        return []
    except Exception as e:
      self._print("Failed to fetch! " + str(e))
      return []

  def getFilesFromFolder(self, folderId : int) -> list[File]:
    """Fetches the files within a specified folder given the folder ID.

    Args:
      folderId (int): The folder ID to fetch the files from.

    Returns:
      list: The list of files in the specified folder, in JSON format.
    """
    try:
      response = self.fetchCanvasAPI(f'folders/{folderId}/files')
      if response.status_code == 200:
        text = response.json()
        return File.fromApiArray(list(text))
      else:
        self._print(f"{color.RED}Could not fetch files from folder ID {folderId}{color.END}")
        return []
    except Exception as e:
      self._print("Failed to fetch! " + str(e))
      return []

  def download(self, courseListWithFiles : list[Course]):
    """Downloads the files within the file list one-by-one, and saves into the folder specified by the root directory.

    Args:
      courseListWithFiles (list): The list of files to download, organised by course and folder as a list of course objects containing the folders and files to download.
    """

    self._print(color.UNDERLINE + color.BOLD + f"Downloading files:" + color.END)
    pathlib.Path(f"{self.root}").mkdir(parents=True, exist_ok=True)
    fileLogLocation = f'{self.root}/.files'

    fileLog = FileLog.fromFileLog(fileLogLocation)

    for course in courseListWithFiles:
      folders = course.folders
      courseNameUsed = course.course_code.replace('/', '')
      
      self._print()
      self._print(color.BOLD + f"Course: {course.name} ({course.course_code})" + color.END)

      for folder in folders:
        path = folder.getPath()
        self._print(f"Processing {courseNameUsed}{path}...")
        pathlib.Path(f"{self.root}/{courseNameUsed}{path}").mkdir(parents=True, exist_ok=True)

        fileList = folder.files
        for file in fileList:
          if fileLog.isPresent(file):
            if fileLog.isUpdated(file):
              self._print(f"{color.YELLOW}No updates required for file ID {file.id}: {file.display_name}{color.END}")
            else:
              fileLog.update(file.uuid, file.modified_at)
              downloadStatus = file.download(f"{self.root}/{courseNameUsed}{path}")
              if downloadStatus:
                self._print(f"{color.GREEN}Updated file ID {file.id}: {file.display_name}{color.END}")
              else:
                self._print("Failed to download!")
          else:
            fileLog.append(file.uuid, file.modified_at)
            downloadStatus = file.download(f"{self.root}/{courseNameUsed}{path}")
            if downloadStatus:
              self._print(f"{color.GREEN}Added file ID {file.id}: {file.display_name}{color.END}")
            else:
              self._print("Failed to download!")
    fileLog.saveToFileLog(fileLogLocation)
    self._print()
    self._print(color.GREEN + color.BOLD + f"Download complete" + color.END)

  def run(self):
    """
    Runs the current downloader by loading the courses/folders/files, then downloading the files loaded.
    """

    self.displayArea.delete(1.0, tk.END)
    courseListWithFiles = self.loadFiles()
    self.download(courseListWithFiles)