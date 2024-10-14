# canvas-downloader

Downloads files from Canvas straight to your computer, into a directory you specify.

<img alt="Canvas downloader GUI" src="https://brein62.github.io/projects/canvas-downloader.png" height="30%" width="30%" />

## Initialising the app

1. You need Python 3.8 and above installed on your computer.
2. In the terminal, run the command ```pip install requests``` and ```pip install python-dotenv``` to install this application's dependencies.
3. You should be able to run the app now!

## Running the app

1. You can run the app by running the command ```python ./main.py``` in the directory containing the code.
You should see a GUI where you can specify the Canvas token, Canvas URL, and Canvas file path. Refer to the [Usage Notes](#usage-notes) section below for more information.
2. Take note that the app will take a few minutes to download all the files. **With the current implementation, files containing the same name in the folder will be overwritten. You can safely create new files if they do not have the same name as any file on Canvas.**
3. The app will produce a log of the files downloaded in the root folder, named `.files`. (e.g. if you saved the Canvas files on the desktop, then there will be a `.files` log on the desktop). If you want to ensure that all the files are re-downloaded, you may remove the `.files` log on your own or click on the `Clear File Log` button in the application.
4. You may use the `Course Filters` dialog to adjust the courses you want to download. If not, files will be downloaded from all of your
currently loaded courses on Canvas.

## Usage notes

1. **Canvas Token**: The **Canvas token** to use for the Canvas downloader.
                       Can be accessed in Canvas using [this tutorial](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273).
                       This token will not be stored and only saved on your computer, so your Canvas data is safe.
2. **Canvas URL**: The URL of the Canvas installation, without any slash at
                       the back (example: `https://canvas.nus.edu.sg`)
3. **Canvas File Path**: The path in your computer to save the Canvas files to (example: `./test_files`).