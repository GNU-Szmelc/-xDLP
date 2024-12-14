#!/usr/bin/python3
# Simple app to search on YouTube
# With playlists and player capabilities!
# Probably even crossplatform!

import os
import sys
import subprocess
import platform
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from googleapiclient.discovery import build
import requests

# API Key
api_key = "AIzaSyCSVVoqQohX0L7BUIfyitjF9GrOgpA1MTE"

# SETTINGS
maxresults = 20
g1, g2, g3, g4 = 650, 150, 500, 800
pcodec = "mp3"
pquality = "192"
mp = "mpv"
mpc = "--play-and-exit"
defaud, defvid = "mp3", "mp4"
b1n, b2n = "Play Fullscreen", "Play Audio"

# Detect Platform
current_os = platform.system()
is_windows = current_os == "Windows"
is_mac = current_os == "Darwin"
is_linux = current_os == "Linux"

# Cross-platform command helper
def run_command(command):
    if is_windows:
        subprocess.run(command, shell=True)
    else:
        os.system(command)

# Install google-api-client if not present
try:
    from googleapiclient.discovery import build
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client"])


class YTDLPInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_directory = os.path.expanduser("~")  # Default to $HOME
        self.audio_process = None
        self.thumbnail_urls = []  # Ensure this is initialized
        self.initUI()

    def initUI(self):
        self.setWindowTitle('[$xDLP] ~ FOSS-YT Client v4')
        self.setGeometry(g1, g2, g3, g4)

        vbox = QVBoxLayout()

        # URL Input
        self.url_label = QLabel('Enter URL:')
        self.url_input = QLineEdit()
        hbox_url = QHBoxLayout()
        hbox_url.addWidget(self.url_label)
        hbox_url.addWidget(self.url_input)
        vbox.addLayout(hbox_url)

        # Search Input and Directory Button
        self.search_label = QLabel('Search YouTube:')
        self.search_input = QLineEdit()
        self.choose_directory_button = QPushButton('Search')
        self.choose_directory_button.clicked.connect(self.search_youtube)
        hbox_search = QHBoxLayout()
        hbox_search.addWidget(self.search_label)
        hbox_search.addWidget(self.search_input)
        hbox_search.addWidget(self.choose_directory_button)
        vbox.addLayout(hbox_search)

        # Search Button
        self.search_button = QPushButton('Choose Directory')
        self.search_button.clicked.connect(self.select_directory)
        vbox.addWidget(self.search_button)

        # Thumbnail Display
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.thumbnail_label)

        # Search Results
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(self.clicked_item_changed)
        self.search_results.currentRowChanged.connect(self.update_item_details)
        vbox.addWidget(self.search_results)

        # Bottom Buttons - Row 1
        hbox_bottom1 = QHBoxLayout()
        self.options_button1 = QPushButton('One ' + defvid)
        self.options_button1.clicked.connect(self.download_one_mp4)
        hbox_bottom1.addWidget(self.options_button1)

        self.options_button2 = QPushButton('One ' + defaud)
        self.options_button2.clicked.connect(self.download_one_wav)
        hbox_bottom1.addWidget(self.options_button2)
        vbox.addLayout(hbox_bottom1)

        # Bottom Buttons - Row 2
        hbox_bottom2 = QHBoxLayout()
        self.options_button3 = QPushButton('Playlist ' + defvid)
        self.options_button3.clicked.connect(self.download_playlist_mp4)
        hbox_bottom2.addWidget(self.options_button3)

        self.options_button4 = QPushButton('Playlist ' + defaud)
        self.options_button4.clicked.connect(self.download_playlist_wav)
        hbox_bottom2.addWidget(self.options_button4)
        vbox.addLayout(hbox_bottom2)

        # Custom Buttons - Row 3
        hbox_bottom3 = QHBoxLayout()
        custom_button1 = QPushButton(b1n)
        custom_button1.clicked.connect(self.custom_button1_action)
        hbox_bottom3.addWidget(custom_button1)

        custom_button2 = QPushButton(b2n)
        custom_button2.clicked.connect(self.custom_button2_action)
        hbox_bottom3.addWidget(custom_button2)

        vbox.addLayout(hbox_bottom3)

        self.setLayout(vbox)

    # Custom Button Actions
    def custom_button1_action(self):
        url = self.url_input.text()
        if is_windows:
            run_command(f'start {mp} --fs "{url}"')
        elif is_mac:
            run_command(f'open -a {mp} --args --fs "{url}"')
        else:  # Linux
            run_command(f'{mp} --fs "{url}"')

    def custom_button2_action(self):
        url = self.url_input.text()
        if is_windows:
            run_command(f'start {mp} --no-video "{url}"')
        elif is_mac:
            run_command(f'open -a {mp} --args --no-video "{url}"')
        else:  # Linux
            run_command(f'{mp} --no-video "{url}"')

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selected_directory = directory

    def run_ytdlp_command(self, args):
        if self.selected_directory:
            args.extend(["-o", f"{self.selected_directory}/%(title)s.%(ext)s"])
        if is_windows:
            subprocess.run(args, shell=True)
        else:
            subprocess.call(args)

    # Search YouTube
    def search_youtube(self):
        search_query = self.search_input.text()
        results = self.perform_youtube_search(search_query)
        self.update_search_results(results)

    def perform_youtube_search(self, search_query):
        youtube = build("youtube", "v3", developerKey=api_key)
        params = {"q": search_query, "maxResults": maxresults, "part": "snippet", "type": "video"}
        response = youtube.search().list(**params).execute()

        search_results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail_url = item["snippet"]["thumbnails"]["default"]["url"]
            search_results.append((title, video_url, thumbnail_url))

        return search_results

    def update_search_results(self, results):
        self.search_results.clear()
        self.thumbnail_urls = []

        for title, video_url, thumbnail_url in results:
            item = QListWidgetItem(title)
            item.setData(32, video_url)
            self.search_results.addItem(item)
            self.thumbnail_urls.append(thumbnail_url)

    def clicked_item_changed(self, clicked_item):
        if clicked_item:
            current_row = self.search_results.row(clicked_item)
            self.update_item_details(current_row)

    def update_item_details(self, current_row):
        if current_row >= 0:  # Ensure the row index is valid
            clicked_item = self.search_results.item(current_row)
            video_url = clicked_item.data(32)
            self.url_input.setText(video_url)

            # Display the thumbnail
            thumbnail_url = self.thumbnail_urls[current_row]
            response = requests.get(thumbnail_url)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.thumbnail_label.setPixmap(pixmap.scaledToHeight(200))

    # Download Methods
    def download_one_mp4(self):
        self.run_ytdlp_command(["yt-dlp", "--format", defvid, self.url_input.text()])

    def download_one_wav(self):
        self.run_ytdlp_command(["yt-dlp", "--extract-audio", "--audio-format", defaud, self.url_input.text()])

    def download_playlist_mp4(self):
        self.run_ytdlp_command(["yt-dlp", "--yes-playlist", "--format", defvid, self.url_input.text()])

    def download_playlist_wav(self):
        self.run_ytdlp_command(["yt-dlp", "--yes-playlist", "--extract-audio", "--audio-format", defaud, self.url_input.text()])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = YTDLPInterface()
    interface.show()
    sys.exit(app.exec_())
