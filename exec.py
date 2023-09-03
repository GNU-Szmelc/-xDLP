import sys
import subprocess
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget, QListWidgetItem

class YTDLPInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('$-dlp YT client')

        vbox = QVBoxLayout()

        self.url_label = QLabel('Enter Media URL:')
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
        self.search_results.itemClicked.connect(self.item_selected)
        vbox.addWidget(self.search_results)

        self.directory_label = QLabel('Select download directory:')
        vbox.addWidget(self.directory_label)

        self.directory_button = QPushButton('Select Directory')
        self.directory_button.clicked.connect(self.select_directory)
        vbox.addWidget(self.directory_button)

        self.options_label = QLabel('Select download option:')
        vbox.addWidget(self.options_label)

        self.options_button1 = QPushButton('Single mp4')
        self.options_button1.clicked.connect(self.download_one_mp4)
        vbox.addWidget(self.options_button1)

        self.options_button2 = QPushButton('Single wav')
        self.options_button2.clicked.connect(self.download_one_wav)
        vbox.addWidget(self.options_button2)

        self.options_button3 = QPushButton('Playlist mp4')
        self.options_button3.clicked.connect(self.download_playlist_mp4)
        vbox.addWidget(self.options_button3)

        self.options_button4 = QPushButton('Playlist wav')
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
        for title, video_url in results:
            item = QListWidgetItem(title)
            item.setData(32, video_url)
            self.search_results.addItem(item)

    def search_youtube(self):
        search_query = self.search_input.text()
        results = self.perform_youtube_search(search_query)
        self.update_search_results(results)

    def perform_youtube_search(self, search_query):
        API_KEY = "AIzaSyCSVVoqQohX0L7BUIfyitjF9GrOgpA1MTE"
        MAX_RESULTS = 5

        params = {
            "key": API_KEY,
            "q": search_query,
            "maxResults": MAX_RESULTS,
            "part": "snippet",
            "type": "video"
        }

        response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)

        search_results = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                search_results.append((title, video_url))
        else:
            print("Error occurred:", response.status_code)

        return search_results

    def item_selected(self, item):
        video_url = item.data(32)
        self.url_input.setText(video_url)

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
    sys.exit(app.exec())
