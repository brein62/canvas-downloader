"""
Contains several model classes for the API Course, Folder, and File,
as well as for the FileLog.

Course, Folder, and File models based on the Canvas REST API
(documentation: https://canvas.instructure.com/doc/api/).

FileLog model acts as a wrapper around a list of File objects, to
be saved and loaded from locally-stored file logs (`.files`).
"""

import requests
import sys

if sys.version_info < (3, 10):
    from typing_extensions import Self
else:
    from typing import Self


class File:
    """
    Represents a file within a Course's files, based on the File object in
    the Canvas API: https://canvas.instructure.com/doc/api/files.html

    A file contains members `modified_at`, `id`, `url` and `display_name`.
    """

    def __init__(
        self,
        modified_at: str,
        id: int = None,
        url: str = None,
        display_name: str = None,
    ):
        """Creates a File object instance.

        Args:
          modified_at (str): The last modified at date for the file from the Canvas API.
          id (int): The ID of the file, from the Canvas API.
          url (str): The URL of the file contents to download, from the Canvas API.
          display_name (str): The file's display name on Canvas.
        """
        self.modified_at = modified_at
        self.id = id
        self.url = url
        self.display_name = display_name

    @classmethod
    def fromApiArray(cls, apiArray: list[dict]) -> list[Self]:
        """
        A static class method that generates a list of File objects based on a
        list of File JSON objects from the Canvas API. Each Canvas API file
        object must be in the format indicated in
        https://canvas.instructure.com/doc/api/files.html with mandatory fields
        `modified_at`, `id`, `url` and `display_name`.

        Args:
          apiArray (list[dict]): The JSON array from the API to be processed into
          File objects.

        Returns:
          list[File]: The resulting list of File objects from the Canvas API
          JSON output.
        """
        return list(
            map(
                lambda apiObject: cls(
                    modified_at=apiObject["modified_at"],
                    id=apiObject["id"],
                    url=apiObject["url"],
                    display_name=apiObject["display_name"],
                ),
                apiArray,
            )
        )

    def toLoadFileStr(self) -> str:
        """Returns a simplified string representation of the File object to be saved
        in the locally-stored file log (`.files`), in the format "{id} {modified_at}\\n".

        Returns:
          str: The string representation of the File object.
        """
        return f"{self.id} {self.modified_at}\n"

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the File object.

        Returns:
          str: The string representation of the File object.
        """
        return f"File with ID {self.id}, Modified at {self.modified_at}, URL {self.url}, Display name {self.display_name}"

    def __repr__(self) -> str:
        """Returns a string representation of the File object.

        Returns:
          str: The string representation of the File object.
        """
        return f"File({self.id}, {self.modified_at}, {self.url}, {self.display_name})"

    def download(self, path: str) -> bool:
        """Downloads a file by sending a `GET` request to the file and retrieving its content, then
        saving it into the

        Args:
          path (str): The path to save the file into.

        Returns:
          bool: The success status of the download. True if download is successful, false otherwise.
        """
        if self.url is None:
            return False

        if path[-1] != "/":
            path += "/"

        try:
            response = requests.get(self.url)
            content = response.content

            f = open(f"{path}{self.display_name}", "wb")
            if content != None:
                f.write(content)
            f.close()
        except:
            return False

        return True


class Folder:
    """
    Represents a folder within a Course's files, based on the Folder object in
    the Canvas API: https://canvas.instructure.com/doc/api/files.html

    A folder contains members `id` and `full_name` (from the API Folder object)
    and `files` which are the list of files within the folder.
    """

    def __init__(self, id: int, full_name: str, files: list[File] = None):
        """Creates a Folder object instance.

        Args:
          id (int): The ID of the folder, from the Canvas API.
          full_name (str): The full name (path) of the folder.
          files (list[File]): The list of files within the folder (as a list of File objects).
        """
        self.id = id
        self.full_name = full_name
        self.files = files

    def getPath(self) -> str:
        """
        Returns the path of the Folder within a course's files. Note that the Canvas API adds
        a root folder of `course files` for all courses which is removed in this function. However,
        since the root folder for each course is the course code when downloading the files,
        the `course files` folder is stripped from the full path when files are downloaded.

        Returns:
          str: The path of the Folder within a course's files after stripping away the `course files` root folder.
        """
        path = self.full_name[12:] if len(self.full_name) > 12 else "/"
        return path

    def withFiles(self, files: list[File]) -> Self:
        """
        Returns a new Folder object instance with a list of File objects representing the files
        present in the specific folder.

        Args:
          files (list[File]): The list of File objects to be included in the new Folder instance.

        Returns:
          Folder: The new Folder object instance with the list of files being set.
        """
        return Folder(self.id, self.full_name, files)

    @classmethod
    def fromApiArray(cls, apiArray: list[dict]) -> list[Self]:
        """
        A static class method that generates a list of Folder objects based on a
        list of Folder JSON objects from the Canvas API. Each Canvas API folder
        object must be in the format indicated in
        https://canvas.instructure.com/doc/api/files.html with mandatory fields
        `id` and `full_name`.

        Args:
          apiArray (list[dict]): The JSON array from the API to be processed into
          Folder objects.

        Returns:
          list[Folder]: The resulting list of Folder objects from the Canvas API
          JSON output.
        """
        return list(
            map(
                lambda apiObject: cls(
                    id=apiObject["id"], full_name=apiObject["full_name"]
                ),
                apiArray,
            )
        )

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the Folder object.

        Returns:
          str: The string representation of the Folder object.
        """
        return (
            f"Folder with ID {self.id}, path {self.full_name}, and files {self.files}"
        )

    def __repr__(self) -> str:
        """Returns a string representation of the Folder object.

        Returns:
          str: The string representation of the Folder object.
        """
        return f"Folder({self.id}, {self.full_name}, {self.files})"


class Course:
    """
    Course model for this application, based on the Course object in the API:
    https://canvas.instructure.com/doc/api/courses.html

    A course contains members `id`, `name` and `course_code` (from the API Course object), and
    `folders` that represent the folders within this course.
    """

    def __init__(
        self, id: int, name: str, course_code: str, folders: list[Folder] = None
    ):
        """Creates a Course object instance.

        Args:
          id (int): The ID of the course, from the Canvas API.
          name (str): The full name of the course.
          course_code (str): The course code.
          folders (list[Folder]): The list of Folder objects the Course contains.
        """
        self.id = id
        self.name = name
        self.course_code = course_code
        self.folders = folders

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the Course object.

        Returns:
          str: The string representation of the Course object.
        """
        return f"Course with ID {self.id}, Name {self.name}, Code {self.course_code}, folders {self.folders}"

    def __repr__(self) -> str:
        """Returns a string representation of the Course object.

        Returns:
          str: The string representation of the Course object.
        """
        return f"Course({self.id}, {self.name}, {self.course_code}, {self.folders})"

    def withFolders(self, folders: list[Folder]) -> Self:
        """
        Returns a new Course object instance with a list of Folder objects representing the folders
        present in the specific course.

        Args:
          folders (list[Folder]): The list of Folder objects to be included in the new Course instance.

        Returns:
          Course: The new Course object instance with the list of folders being set.
        """
        return Course(self.id, self.name, self.course_code, folders)

    @classmethod
    def fromApiArray(cls, apiArray: list[dict]) -> list[Self]:
        """
        A static class method that generates a list of Course objects based on a
        list of Course JSON objects from the Canvas API. Each Canvas API course
        object must be in the format indicated in
        https://canvas.instructure.com/doc/api/courses.html with mandatory fields
        `id`, `name`, and `course_code`.

        Args:
          apiArray (list[dict]): The JSON array from the API to be processed into
          Course objects.

        Returns:
          list[Course]: The resulting list of Course objects from the Canvas API
          JSON output.
        """
        return list(
            map(
                lambda apiObject: cls(
                    id=apiObject["id"],
                    name=apiObject["name"],
                    course_code=apiObject["course_code"],
                ),
                apiArray,
            )
        )


class FileLog:
    """Represents a file log (`.files`) stored locally that contains files. A wrapper
    around a list of File objects.
    """

    def __init__(self, fileList: list[File] = None):
        """Creates a new FileLog object.

        Args:
          fileList (list[File]): The file list to initialise the file log with.
        """
        self.fileList = fileList

    @classmethod
    def fromFileLog(cls, fileLogLocation: str) -> Self:
        """
        A static class method that generates a file log object based on  the
        locally-stored file log(`.files`).

        Args:
          fileLogLocation (str): The location of the file log that should contain
          the File objects.

        Returns:
          list[File]: The resulting list of File objects from the file log. If the
          file log doesn't exist or the file log is empty/invalid, returns an
          empty array.
        """

        loadedFiles: list[str] = []

        try:
            fileLog = open(fileLogLocation, "r")
            loadedLines = fileLog.readlines()
            fileLog.close()

            for line in loadedLines:
                id, modified_at = line.strip().split(" ")[:2]
                loadedFiles.append(File(id=id, modified_at=modified_at))

        except:
            loadedFiles = []

        return cls(fileList=loadedFiles)

    def saveToFileLog(self, fileLogLocation: str):
        """Saves the list of files in the file log to a local file. Each file is saved
        as a line with the format "{id} {modified_at}\\n".

        Args:
          fileLogLocation (str): The path of the file to save the list of files into.
        """
        fileLog = open(fileLogLocation, "w")

        for file in self.fileList:
            fileLog.write(file.toLoadFileStr())

        fileLog.close()

    def findById(self, id: int) -> File:
        """Finds the first file in the file log with a specified ID. Note that ID
        is unique, so the first file should be the first file desired.

        Args:
          id (int): The ID of the file to find within the file log.

        Returns:
          File: The file within the file log, if found, else None.
        """
        for file in self.fileList:
            if file.id == id:
                return file

        return None

    def append(self, id: int, modified_at: str):
        """Appends a new File to the file log given its `id` and `modified_at`
        parameters.

        Args:
          id (int): The ID of the new file to append to the file log.
          modified_at (str): The modified at timestamp of the new file to append to the file log.
        """
        self.fileList.append(File(id, modified_at))

    def update(self, id: int, modified_at: str):
        """Updates the modified at timestamp of the file in the file log, identified by ID. If
        the file is not present in the file log, appends the file into the file log.

        Args:
          id (int): The ID of the file in the file log to update the modified at timestamp.
          modified_at (str): The new modified at timestamp.
        """
        fileInLog = self.findById(id)

        if fileInLog is None:
            self.append(id, modified_at)
        else:
            fileInLog.modified_at = modified_at

    def isUpdated(self, file: File) -> bool:
        """Checks whether the file given has been updated in the file log.

        Args:
          file (File): The file to check.

        Returns:
          bool: True if the file is the most updated based on modified at timestamp, False otherwise
        """
        loadedFile = self.findById(file.id)

        if loadedFile:
            return loadedFile.modified_at == file.modified_at
        else:
            return False

    def isPresent(self, file: File) -> bool:
        """Checks whether the given file is present in the file log.

        Args:
            file (File): The file to be checked for presence in the file log.

        Returns:
            bool: True if file is present in the file log, False otherwise
        """
        loadedFile = self.findById(file.id)

        return loadedFile is not None
