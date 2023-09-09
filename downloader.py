import requests
import pathlib
import tkinter as tk

class color:
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

    displayArea.delete(1.0, tk.END)

    downloader = Downloader(canvasUrl, canvasToken, displayWindow, displayArea)

    fileList = downloader.loadFiles()

    downloader.download(fileList, root)

class Downloader:
    def __init__(self, canvasUrl : str, canvasToken : str, displayWindow : tk.Tk = None, displayArea : tk.Text = None):
        self.canvasUrl = canvasUrl
        self.canvasToken = canvasToken
        self.displayWindow = displayWindow
        self.displayArea = displayArea

    def _print(self, content : str = ""):
        print(content)
        if self.displayWindow != None and self.displayArea != None:
            if content.startswith(color.BOLD):
                self.displayArea.insert(tk.END, content[4:-4] + "\n", "bold")
            else:
                self.displayArea.insert(tk.END, content + "\n")
            self.displayWindow.update_idletasks()

    def loadFiles(self):
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

    def fetchCanvasAPI(self, apiPath : str):
        response = requests.get(
            f"{self.canvasUrl}/api/v1/{apiPath}?per_page=1000&access_token={self.canvasToken}",
            headers={
                'Accept': 'application/json'
            }    
        )
        return response

    def fetchCourses(self):
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
        
    def getCourseFolders(self, courseId : int):
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

    def getFilesFromFolder(self, folderId : int):
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
        try:
            response = requests.get(url)
            return response.content
        except:
            self._print("Failed to download!")
            return None

    def download(self, fileList : list, root : str):
        """Downloads the files within the file list one-by-one, and saves into the folder specified by the root directory."""

        try:
            fileLog = open('.files', 'r')
            loadedFiles = fileLog.readlines()
            fileLog.close()
        except:
            loadedFiles = []

        for courses in fileList:
            course = courses['course']
            folders = courses['folders']
            courseNameUsed = course['course_code'].replace('/', '')

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
                                f.write(content)
                                f.close()
                            else:
                                self._print(f"File ID {file['id']} is already updated!")
                            fileFoundInLoadedFiles = True
                            break
                    
                    if not fileFoundInLoadedFiles:
                        loadedFiles.append(file['uuid'] + " " + file['modified_at'] + '\n')
                        content = self.downloadFile(file['url'])
                        f = open(f"{root}/{courseNameUsed}{path}/{file['display_name']}", "wb")
                        f.write(content)
                        f.close()

        fileLog = open('.files', 'w')
        for i in range(len(loadedFiles) - 1):
            if not loadedFiles[i].endswith('\n'): 
                loadedFiles[i] += '\n'
        fileLog.writelines(loadedFiles)
        fileLog.close()

    def download_test(self, fileList : list, root : str):
        """Simulates a downloader without performing the full and slow process of downloading the files."""
        for courses in fileList:
            course = courses['course']
            folders = courses['folders']
            courseNameUsed = course['course_code'].replace('/', '')

            for folder in folders:
                path = folder['full_name'][12:] if len(folder) > 12 else '/'
                self._print(f"Processing {root}/{courseNameUsed}{path}...")

                fileList = folder['files']
                for file in fileList:
                    self._print(f"Downloaded file path: {root}/{courseNameUsed}{path}/{file['display_name']} from URL {file['url']}")