"""The main entry point to the application."""

import os
from downloader import Downloader
from gui import runGui

from dotenv import load_dotenv

load_dotenv()

root = os.environ.get('SAVE_TO')
canvasUrl = os.environ.get('CANVAS_URL')
canvasToken = os.environ.get('CANVAS_TOKEN')

if __name__ == "__main__": 
  runGui()