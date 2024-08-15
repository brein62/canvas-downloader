import requests
import pathlib
import tkinter as tk
import os

os.system("")

"""
File lists are currently being processed in the following JSON format:
[
    {
        "courses": course_name,
        "folders": [
            {
                /* folder data from Canvas API */,
                "files": [
                    /* file data from Canvas API */
                ]
            },
            ...
        ]
    },
    ...
]
"""

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

    fileList = downloader.loadFiles()

    downloader.download(fileList, root)

class Downloader:
    """A class representing a Canvas file downloader."""

    def __init__(self, canvasUrl : str, canvasToken : str, displayWindow : tk.Tk = None, displayArea : tk.Text = None):
        self.canvasUrl = canvasUrl
        self.canvasToken = canvasToken
        self.displayWindow = displayWindow
        self.displayArea = displayArea

    def _print(self, content : str = ""):
        """Prints a status line regarding the Canvas file download process in the console as well as in the
        textarea within the GUI.

        Args:
            content (str, optional): The content to be displayed. Defaults to "".
        """
        print(content)
        if self.displayWindow != None and self.displayArea != None:
            if content.startswith(color.BOLD):
                self.displayArea.insert(tk.END, content[4:-4] + "\n", "bold")
            else:
                self.displayArea.insert(tk.END, content + "\n")
            self.displayWindow.update_idletasks()

    def loadFiles(self) -> list:
        """Gets the courses and files and organises the files to download in a JSON format.

        Returns:
            list: The list of files, organised by course and folder in a JSON format.
        """
        self._print(color.BOLD + f"Retrieving files from courses:" + color.END)
        self._print()
        fileList = []
        for course in self.fetchCourses():
            self._print(color.BOLD + f"Course: {course['name']} ({course['course_code']})" + color.END)
            foldersArray = []
            for folder in self.getCourseFolders(course['id']):
                courseFolderName = folder['full_name'][12:]
                filesInFolder = self.getFilesFromFolder(folder['id'])
                self._print(str(folder['id']) + " " + courseFolderName if courseFolderName != '' else '/')
                #self._print('\t'.join(list(map(lambda file: file['display_name'], filesInFolder))))
                foldersArray.append({**folder, "files": filesInFolder})
            self._print()
            fileList.append({ "course": course, "folders": foldersArray })
        return fileList

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

    def fetchCourses(self) -> list:
        """Fetches the user's courses as a JSON list.

        Returns:
            list: The list of courses by the user, in JSON format.
        """
        try:
            response = self.fetchCanvasAPI('courses')
            if response.status_code == 200:
                text = response.json()
                return list(filter(lambda course : 'name' in course.keys() and course['name'] != None, text))
            else:
                self._print(f"Could not fetch courses! HTTP status: {response.status_code}")
                return []
        except Exception as e:
            self._print("Failed to fetch! " + str(e))
            return []
        
    def getCourseFolders(self, courseId : int) -> list:
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
                return list(text)
            else:
                self._print(f"Could not fetch folders from course ID {courseId}")
                return []
        except Exception as e:
            self._print("Failed to fetch! " + str(e))
            return []

    def getFilesFromFolder(self, folderId : int) -> list:
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
                return list(text)
            else:
                self._print(f"Could not fetch files from folder ID {folderId}")
                return []
        except Exception as e:
            self._print("Failed to fetch! " + str(e))
            return []

    def downloadFile(self, url : str):
        """Downloads a file by sending a `GET` request to the file and retrieving its content.

        Args:
            url (str): The URL to download the file from.

        Returns:
            The content of the file.
        """
        try:
            response = requests.get(url)
            return response.content
        except:
            self._print("Failed to download!")
            return None

    def download(self, fileList : list, root : str):
        """Downloads the files within the file list one-by-one, and saves into the folder specified by the root directory.

        Args:
            fileList (list): The list of files to download, organised by course and folder as returned by `loadFiles`.
            root (str): The root directory to save the files downloaded into.
        """

        self._print(color.BOLD + f"Downloading files:" + color.END)
        fileLogLocation = f'{root}/.files'

        try:
            fileLog = open(fileLogLocation, 'r')
            loadedFiles = fileLog.readlines()
            fileLog.close()
        except:
            loadedFiles = []

        for courses in fileList:
            course = courses['course']
            folders = courses['folders']
            courseNameUsed = course['course_code'].replace('/', '')
            
            self._print()
            self._print(color.BOLD + f"Course: {course['name']} ({course['course_code']})" + color.END)

            for folder in folders:
                path = folder['full_name'][12:] if len(folder) > 12 else '/'
                self._print(f"Processing {courseNameUsed}{path}...")
                pathlib.Path(f"{root}/{courseNameUsed}{path}").mkdir(parents=True, exist_ok=True)

                fileList = folder['files']
                for file in fileList:

                    fileFoundInLoadedFiles = False

                    for i in range(len(loadedFiles)):
                        if loadedFiles[i].strip().startswith(file['uuid']):
                            if not loadedFiles[i].strip().endswith(file['modified_at']):
                                loadedFiles[i] = file['uuid'] + " " + file['modified_at'] + '\n'
                                content = self.downloadFile(file['url'])
                                f = open(f"{root}/{courseNameUsed}{path}/{file['display_name']}", "wb")
                                if content != None:
                                    f.write(content)
                                f.close()
                                self._print(f"Updated file ID {file['id']}")
                            else:
                                self._print(f"No updates required for file ID {file['id']}")
                            fileFoundInLoadedFiles = True
                            break
                    
                    if not fileFoundInLoadedFiles:
                        loadedFiles.append(file['uuid'] + " " + file['modified_at'] + '\n')
                        content = self.downloadFile(file['url'])
                        f = open(f"{root}/{courseNameUsed}{path}/{file['display_name']}", "wb")
                        if content != None:
                            f.write(content)
                        f.close()
                        self._print(f"Added file ID {file['id']}")

        fileLog = open(fileLogLocation, 'w')
        for i in range(len(loadedFiles) - 1):
            if not loadedFiles[i].endswith('\n'): 
                loadedFiles[i] += '\n'
        fileLog.writelines(loadedFiles)
        fileLog.close()