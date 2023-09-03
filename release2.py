import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap
from googleapiclient.discovery import build
import requests
from PyQt5.QtCore import Qt

class YTDLPInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('[$xDLP] ~ Less Shitty YT Client')

        vbox = QVBoxLayout()

        self.url_label = QLabel('Enter URL:')
        vbox.addWidget(self.url_label)

        self.url_input = QLineEdit()
        vbox.addWidget(self.url_input)

        self.search_label = QLabel('Search YouTube:')
        vbox.addWidget(self.search_label)

        self.search_input = QLineEdit()
        vbox.addWidget(self.search_input)

        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.search_youtube)
        vbox.addWidget(self.search_button)

        self.search_results = QListWidget()
        self.search_results.currentItemChanged.connect(self.display_thumbnail)
        self.search_results.itemEntered.connect(self.hovered_item_changed)  # Connect itemEntered signal
        self.search_results.itemClicked.connect(self.clicked_item_changed)  # Connect itemClicked signal
        vbox.addWidget(self.search_results)

        self.thumbnail_label = QLabel()  # Display thumbnail here
        vbox.addWidget(self.thumbnail_label)  # Add thumbnail label to layout

        self.directory_label = QLabel('Select download directory:')
        vbox.addWidget(self.directory_label)

        self.directory_button = QPushButton('Select Directory')
        self.directory_button.clicked.connect(self.select_directory)
        vbox.addWidget(self.directory_button)

        self.options_label = QLabel('Select download option:')
        vbox.addWidget(self.options_label)

        self.options_button1 = QPushButton('Single Mp4')
        self.options_button1.clicked.connect(self.download_one_mp4)
        vbox.addWidget(self.options_button1)

        self.options_button2 = QPushButton('Single Wav')
        self.options_button2.clicked.connect(self.download_one_wav)
        vbox.addWidget(self.options_button2)

        self.options_button3 = QPushButton('Playlist Mp4')
        self.options_button3.clicked.connect(self.download_playlist_mp4)
        vbox.addWidget(self.options_button3)

        self.options_button4 = QPushButton('Playlist Wav')
        self.options_button4.clicked.connect(self.download_playlist_wav)
        vbox.addWidget(self.options_button4)

        self.setLayout(vbox)

        self.selected_directory = None

    def select_directory(self):
        self.selected_directory = QFileDialog.getExistingDirectory(self, "Select Directory")

    def run_ytdlp_command(self, args):
        if self.selected_directory:
            args.extend(["-o", f"{self.selected_directory}/%(title)s.%(ext)s"])
        subprocess.call(args)

    def update_search_results(self, results):
        self.search_results.clear()
        self.thumbnail_label.clear()
        self.thumbnail_urls = []  # Store thumbnail URLs for display
        for title, video_url, thumbnail_url in results:
            item = QListWidgetItem(title)
            item.setData(32, video_url)
            item.setData(Qt.UserRole, thumbnail_url)  # Use Qt.UserRole for compatibility
            self.search_results.addItem(item)
            self.thumbnail_urls.append(thumbnail_url)

    def display_thumbnail(self, selected_item):
        if selected_item:
            thumbnail_url = self.thumbnail_urls[self.search_results.row(selected_item)]
            thumbnail_pixmap = self.get_thumbnail_pixmap(thumbnail_url)
            self.thumbnail_label.setPixmap(thumbnail_pixmap)

    def hovered_item_changed(self, hovered_item):
        if hovered_item:
            video_url = hovered_item.data(32)
            self.url_input.setText(video_url)  # Update URL search field when hovered over an item

    def clicked_item_changed(self, clicked_item):
        if clicked_item:
            video_url = clicked_item.data(32)
            self.url_input.setText(video_url)  # Update URL search field when an item is clicked

    def search_youtube(self):
        search_query = self.search_input.text()
        results = self.perform_youtube_search(search_query)
        self.update_search_results(results)

    def perform_youtube_search(self, search_query):
        API_KEY = "AIzaSyCSVVoqQohX0L7BUIfyitjF9GrOgpA1MTE"  # Replace with your API key
        youtube = build("youtube", "v3", developerKey=API_KEY)

        MAX_RESULTS = 10
        params = {
            "q": search_query,
            "maxResults": MAX_RESULTS,
            "part": "snippet",
            "type": "video"
        }
        response = youtube.search().list(**params).execute()

        search_results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail_url = self.get_highest_resolution_thumbnail(youtube, video_id)
            search_results.append((title, video_url, thumbnail_url))

        return search_results

    def get_highest_resolution_thumbnail(self, youtube, video_id):
        response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        thumbnails = response["items"][0]["snippet"]["thumbnails"]
        highest_res_thumbnail = thumbnails.get("maxres") or thumbnails.get("high") or thumbnails.get("medium")
        return highest_res_thumbnail["url"] if highest_res_thumbnail else ""

    def get_thumbnail_pixmap(self, thumbnail_url):
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            pixmap = pixmap.scaledToHeight(200, Qt.FastTransformation)  # Scale the pixmap to fit the thumbnail label
            return pixmap
        else:
            print("Error fetching thumbnail:", response.status_code)
            return QPixmap()  # Return an empty pixmap

    def item_selected(self, item):
        video_url = item.data(32)
        self.url_input.setText(video_url)
        self.display_thumbnail(item)

    def download_one_mp4(self):
        url = self.url_input.text()
        self.run_ytdlp_command(["yt-dlp", url, "--format", "mp4", "--playlist-end", "1"])

    def download_one_wav(self):
        url = self.url_input.text()
        self.run_ytdlp_command(["yt-dlp", url, "--extract-audio", "--audio-format", "wav", "--playlist-end", "1"])

    def download_playlist_mp4(self):
        url = self.url_input.text()
        self.run_ytdlp_command(["yt-dlp", url, "--yes-playlist", "--format", "mp4"])

    def download_playlist_wav(self):
        url = self.url_input.text()
        self.run_ytdlp_command(["yt-dlp", "--ignore-errors", "--format", "bestaudio", "--extract-audio", "--audio-format", "wav", url, "--yes-playlist"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = YTDLPInterface()
    interface.show()
    sys.exit(app.exec_())
