"""A module that encapsulates the Canvas file downloader capability.
"""

import requests
import pathlib
import tkinter as tk
import os

from RichText import RichText
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

def runDownloader(root : str, canvasUrl : str, canvasToken : str, displayWindow : tk.Tk = None, displayArea : tk.Text = None):
  """Runs the downloader in the GUI.

  Args:
  root (str): The root directory to save the files downloaded into.
  canvasUrl (str): The Canvas URL.
  canvasToken (str): The user's Canvas token.
  displayWindow (tk.Tk, optional): The GUI window for the entire application. Defaults to None.
  displayArea (tk.Text, optional): The text area (`tk.Text`) to display the status of the download operation. Defaults to None.
  """

  displayArea.delete(1.0, tk.END)

  downloader = Downloader(canvasUrl, canvasToken, displayWindow, displayArea)

  courseListWithFiles = downloader.loadFiles()

  downloader.download(courseListWithFiles, root)

class Downloader:
  """A class representing a Canvas file downloader."""

  def __init__(self, canvasUrl : str, canvasToken : str, displayWindow : tk.Tk = None, displayArea : RichText = None):
    """Creates a Canvas file downloader object.

    Args:
      canvasUrl (str): The Canvas URL to access the API using.
      canvasToken (str): The Canvas Token used to access the Canvas API.
      displayWindow (tk.Tk, optional): The display window for the GUI. Defaults to None.
      displayArea (RichText, optional): The display text area GUI to display the download status onto. Defaults to None.
    """
    self.canvasUrl = canvasUrl
    self.canvasToken = canvasToken
    self.displayWindow = displayWindow
    self.displayArea = displayArea

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

  def download(self, courseListWithFiles : list[Course], root : str):
    """Downloads the files within the file list one-by-one, and saves into the folder specified by the root directory.

    Args:
      courseListWithFiles (list): The list of files to download, organised by course and folder as a list of course objects containing the folders and files to download.
      root (str): The root directory to save the files downloaded into.
    """

    self._print(color.UNDERLINE + color.BOLD + f"Downloading files:" + color.END)
    pathlib.Path(f"{root}").mkdir(parents=True, exist_ok=True)
    fileLogLocation = f'{root}/.files'

    fileLog = FileLog.fromFileLog(fileLogLocation)

    for course in courseListWithFiles:
      folders = course.folders
      courseNameUsed = course.course_code.replace('/', '')
      
      self._print()
      self._print(color.BOLD + f"Course: {course.name} ({course.course_code})" + color.END)

      for folder in folders:
        path = folder.getPath()
        self._print(f"Processing {courseNameUsed}{path}...")
        pathlib.Path(f"{root}/{courseNameUsed}{path}").mkdir(parents=True, exist_ok=True)

        fileList = folder.files
        for file in fileList:
          if fileLog.isPresent(file):
            if fileLog.isUpdated(file):
              self._print(f"{color.YELLOW}No updates required for file ID {file.id}: {file.display_name}{color.END}")
            else:
              fileLog.update(file.uuid, file.modified_at)
              downloadStatus = file.download(f"{root}/{courseNameUsed}{path}")
              if downloadStatus:
                self._print(f"{color.GREEN}Updated file ID {file.id}: {file.display_name}{color.END}")
              else:
                self._print("Failed to download!")
          else:
            fileLog.append(file.uuid, file.modified_at)
            downloadStatus = file.download(f"{root}/{courseNameUsed}{path}")
            if downloadStatus:
              self._print(f"{color.GREEN}Added file ID {file.id}: {file.display_name}{color.END}")
            else:
              self._print("Failed to download!")
    fileLog.saveToFileLog(fileLogLocation)
    self._print()
    self._print(color.GREEN + color.BOLD + f"Download complete" + color.END)