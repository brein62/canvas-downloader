# canvas-downloader

Downloads files from Canvas straight to your computer, into a directory you specify.

## Running the app

1. You need Python 3.5 and above installed on your computer.
2. In the terminal, run the command ```pip install requests``` and ```pip install python-dotenv``` to install this application's dependencies.
3. Then the app can be run as long as all values in the `.env` file are specified, as in the section below.
4. Take note that the app will take a few minutes to download all the files. **With the current implementation, files containing the same name in the folder will be overwritten. You can safely create new files if they do not have the same name as any file on Canvas.**

## Usage notes

Create an ```.env``` file in the directory where the files and code is. You can take a look at the ```.env.example``` file for implementation tips.

1. ```CANVAS_TOKEN```: The **Canvas token** to use for the Canvas downloader.
                       Can be accessed in Canvas using [this tutorial](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273).
                       This token will not be stored and only saved on your computer, so your Canvas data is safe.
2. ```CANVAS_URL```:   The URL of the Canvas installation, without any slash at
                       the back (example: `https://canvas.nus.edu.sg`)
3. ```SAVE_TO```:      The path in your computer to save the Canvas files to (example: `./test_files`).