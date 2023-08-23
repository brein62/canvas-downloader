import requests
import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

root = os.environ.get('SAVE_TO')

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

def getURL(apiPath : str) -> str:
    return 

'''
python doesn't need proxy wtf'''
def fetchCanvasAPI(apiPath : str):
    response = requests.get(
        f"{os.environ.get('CANVAS_URL')}/api/v1/{apiPath}?per_page=1000&access_token={os.environ.get('CANVAS_TOKEN')}",
        headers={
            'Accept': 'application/json'
        }    
    )
    return response

def fetchCourses():
    try:
        response = fetchCanvasAPI('courses')
        print(response.url)
        if response.status_code == 200:
            text = response.json()
            return list(filter(lambda course : 'name' in course.keys() and course['name'] != None, text))
        else:
            print(f"Could not fetch courses! HTTP status: {response.status_code}")
            return []
    except:
        print("Failed to fetch!")
        return []
    
def getCourseFolders(courseId : int):
    try:
        response = fetchCanvasAPI(f'courses/{courseId}/folders')
        if response.status_code == 200:
            text = response.json()
            return list(text)
        else:
            print(f"Could not fetch folders from course ID {courseId}")
            return []
    except:
        print("Failed to fetch!")
        return []

def getFilesFromFolder(folderId : int):
    try:
        response = fetchCanvasAPI(f'folders/{folderId}/files')
        if response.status_code == 200:
            text = response.json()
            return list(text)
        else:
            print(f"Could not fetch files from folder ID {folderId}")
            return []
    except:
        print("Failed to fetch!")
        return []

def downloadFile(url : str):
    try:
        response = requests.get(url)
        return response.content
    except:
        print("Failed to download!")
        return None

def download(LIST_OF_FILES):
    for courses in LIST_OF_FILES:
        course = courses['course']
        folders = courses['folders']
        courseNameUsed = course['course_code'].replace('/', '')

        for folder in folders:
            path = folder['full_name'][12:] if len(folder) > 12 else '/'
            print(f"Processing {courseNameUsed}{path}...")
            pathlib.Path(f"{root}/{courseNameUsed}{path}").mkdir(parents=True, exist_ok=True)

            fileList = folder['files']
            for file in fileList:
                content = downloadFile(file['url'])
                f = open(f"{root}/{courseNameUsed}{path}/{file['display_name']}", "wb")
                f.write(content)
                f.close()

def main():
    LIST_OF_FILES = []
    for course in fetchCourses():
        print(color.BOLD + f"Course: {course['name']} ({course['course_code']})" + color.END)
        foldersArray = []
        for folder in getCourseFolders(course['id']):
            courseFolderName = folder['full_name'][12:]
            filesInFolder = getFilesFromFolder(folder['id'])
            print(folder['id'], courseFolderName if courseFolderName != '' else '/')
            print('\t'.join(list(map(lambda file: file['display_name'], filesInFolder))))
            foldersArray.append({**folder, "files": filesInFolder})
        print()
        LIST_OF_FILES.append({ "course": course, "folders": foldersArray })


    print(LIST_OF_FILES)

    download(LIST_OF_FILES)

if __name__ == "__main__": 
    main()