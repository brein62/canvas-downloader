import requests
import pathlib

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

def runDownloader(root : str, canvasUrl : str, canvasToken : str):
    fileList = []
    downloader = Downloader(canvasUrl, canvasToken)
    for course in downloader.fetchCourses():
        print(color.BOLD + f"Course: {course['name']} ({course['course_code']})" + color.END)
        foldersArray = []
        for folder in downloader.getCourseFolders(course['id']):
            courseFolderName = folder['full_name'][12:]
            filesInFolder = downloader.getFilesFromFolder(folder['id'])
            print(folder['id'], courseFolderName if courseFolderName != '' else '/')
            print('\t'.join(list(map(lambda file: file['display_name'], filesInFolder))))
            foldersArray.append({**folder, "files": filesInFolder})
        print()
        fileList.append({ "course": course, "folders": foldersArray })

    print(fileList)

    downloader.download(fileList, root)

class Downloader:
    def __init__(self, canvasUrl : str, canvasToken : str):
        self.canvasUrl = canvasUrl
        self.canvasToken = canvasToken

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
            print(response.url)
            if response.status_code == 200:
                text = response.json()
                return list(filter(lambda course : 'name' in course.keys() and course['name'] != None, text))
            else:
                print(f"Could not fetch courses! HTTP status: {response.status_code}")
                return []
        except Exception as e:
            print("Failed to fetch! " + str(e))
            return []
        
    def getCourseFolders(self, courseId : int):
        try:
            response = self.fetchCanvasAPI(f'courses/{courseId}/folders')
            if response.status_code == 200:
                text = response.json()
                return list(text)
            else:
                print(f"Could not fetch folders from course ID {courseId}")
                return []
        except Exception as e:
            print("Failed to fetch! " + str(e))
            return []

    def getFilesFromFolder(self, folderId : int):
        try:
            response = self.fetchCanvasAPI(f'folders/{folderId}/files')
            if response.status_code == 200:
                text = response.json()
                return list(text)
            else:
                print(f"Could not fetch files from folder ID {folderId}")
                return []
        except Exception as e:
            print("Failed to fetch! " + str(e))
            return []

    def downloadFile(self, url : str):
        try:
            response = requests.get(url)
            return response.content
        except:
            print("Failed to download!")
            return None

    def download(self, fileList : list, root : str):
        """Downloads the files within the file list one-by-one, and saves into the folder specified by the root directory."""
        for courses in fileList:
            course = courses['course']
            folders = courses['folders']
            courseNameUsed = course['course_code'].replace('/', '')

            for folder in folders:
                path = folder['full_name'][12:] if len(folder) > 12 else '/'
                print(f"Processing {courseNameUsed}{path}...")
                pathlib.Path(f"{root}/{courseNameUsed}{path}").mkdir(parents=True, exist_ok=True)

                fileList = folder['files']
                for file in fileList:
                    content = self.downloadFile(file['url'])
                    f = open(f"{root}/{courseNameUsed}{path}/{file['display_name']}", "wb")
                    f.write(content)
                    f.close()

    def download_test(self, fileList : list, root : str):
        """Simulates a downloader without performing the full and slow process of downloading the files."""
        for courses in fileList:
            course = courses['course']
            folders = courses['folders']
            courseNameUsed = course['course_code'].replace('/', '')

            for folder in folders:
                path = folder['full_name'][12:] if len(folder) > 12 else '/'
                print(f"Processing {root}/{courseNameUsed}{path}...")

                fileList = folder['files']
                for file in fileList:
                    print(f"Downloaded file path: {root}/{courseNameUsed}{path}/{file['display_name']} from URL {file['url']}")