#!/usr/bin/env python3
import os
import re
import sys
import string
import random
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox,
    QProgressBar, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QPainter
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize

# Constants
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
REF = "https://animepahe.ru/"
API = "https://animesam.pages.dev/api/animepahe/sources"
T = 10

try:
    import cloudscraper
    S = cloudscraper.create_scraper()
except:
    S = requests.Session()

def ck():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

H = {"User-Agent": UA, "Referer": REF, "Cookie": f"__ddg2_={ck()}"}

sf = lambda s: "".join(
    c if c in "-_.() %s%s" % (string.ascii_letters, string.digits) else "_" for c in s
).strip()

# Get assets directory relative to this script
BASE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "assets")
)

WINDOW_ICON_PATH = os.path.join(BASE_DIR, "ico.jpg")
GITHUB_ICON_PATH = os.path.join(BASE_DIR, "github.svg")
REDDIT_ICON_PATH = os.path.join(BASE_DIR, "reddit.svg")
HELP_ICON_PATH = os.path.join(BASE_DIR, "help.svg")


# Network & parsing funcs
def se(q):
    r = S.get(f"https://animepahe.ru/api?m=search&q={requests.utils.quote(q)}", headers=H, timeout=15)
    return r.json().get("data", [])[:6] if r.ok else []


def ep(sid):
    e, p = [], 1
    while True:
        r = S.get(
            f"https://animepahe.ru/api?m=release&id={sid}&sort=episode_asc&page={p}",
            headers=H,
        )
        if not r.ok:
            break
        d = r.json().get("data", [])
        if not d:
            break
        e += d
        if p >= r.json().get("last_page", 1):
            break
        p += 1
    return e


def sc(ss, es):
    r = requests.get(f"{API}/{ss}/{es}", headers={"User-Agent": UA})
    return r.json() if r.ok else {}


def pr(js):
    o = {}
    for s in js.get("sources", []):
        ql, url = s.get("quality", ""), s.get("url", "")
        if not ql.lower().startswith("direct"):
            continue
        m = re.search(r"(\d{3,4}p)", ql.lower())
        q = m.group(1) if m else ql
        lg = "Eng Dub" if "eng" in ql.lower() or "eng" in url.lower() else "JP Sub"
        o.setdefault(q, {}).setdefault(lg, []).append(url)
    return o


def dl(s, no, url, pth):
    if os.path.exists(pth):
        return no, True
    h = {"User-Agent": UA, "Referer": REF}
    try:
        with s.get(url, headers=h, stream=True, timeout=30) as r:
            if not r.ok:
                return no, False
            sz = int(r.headers.get("Content-Length") or 0)
            tmp = pth + ".part"
            with open(tmp, "wb") as f:
                for c in r.iter_content(1024 * 64):
                    if c:
                        f.write(c)
            os.replace(tmp, pth)
            return no, True
    except Exception:
        return no, False


class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    progress_percent = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, title, session_id, episodes, lang, quality, output_dir):
        super().__init__()
        self.title = title
        self.session_id = session_id
        self.episodes = episodes
        self.lang = lang
        self.quality = quality
        self.output_dir = output_dir

    def run(self):
        R = requests.Session()
        ag = {}
        eps_data = ep(self.session_id)
        total_eps = len(self.episodes)
        count = 0

        for e in self.episodes:
            self.progress.emit(f"Fetching episode {e} sources.Please be patient.Progress bar is broken :)...")
            ag[e] = pr(sc(self.session_id, eps_data[e - 1]["session"]))
            time.sleep(0.1)

        qm = {}
        for no, g in ag.items():
            for ql in g:
                if self.lang in g[ql]:
                    qm.setdefault(ql, []).append(no)

        if self.quality not in qm:
            self.progress.emit("Selected quality not available.")
            self.finished.emit([])
            return

        selected_eps = [e for e in sorted(qm[self.quality]) if e in self.episodes]
        jobs = []
        for no in selected_eps:
            url = ag[no][self.quality][self.lang][0]
            ext = os.path.splitext(url.split("?")[0])[1] or ".mp4"
            jobs.append(
                (no, url, os.path.join(self.output_dir, f"{sf(self.title)} - Ep{str(no).zfill(3)} - {self.quality}{ext}"))
            )

        downloaded = []
        with ThreadPoolExecutor(max_workers=T) as ex:
            futs = {ex.submit(dl, R, no, u, p): no for no, u, p in jobs}
            for f in as_completed(futs):
                no, ok = f.result()
                count += 1
                percent = int((count / total_eps) * 100)
                self.progress_percent.emit(percent)
                if ok:
                    downloaded.append(no)
                    self.progress.emit(f"Episode {no} downloaded.")
                else:
                    self.progress.emit(f"Episode {no} failed.")

        self.finished.emit(downloaded)


class SideMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        btn_style = """
        QPushButton {
            background-color: #009688;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
            text-align: left;
            border: none;
        }
        QPushButton:hover {
            background-color: #00796B;
        }
        QPushButton:pressed {
            background-color: #004D40;
        }
        """

        icon_size = QSize(24, 24)

        github_btn = QPushButton(" GitHub")
        github_btn.setIcon(QIcon(GITHUB_ICON_PATH))
        github_btn.setIconSize(icon_size)
        github_btn.setStyleSheet(btn_style)
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/NatsukiSubaruGH/anirip"))
        )

        reddit_btn = QPushButton(" Reddit")
        reddit_btn.setIcon(QIcon(REDDIT_ICON_PATH))
        reddit_btn.setIconSize(icon_size)
        reddit_btn.setStyleSheet(btn_style)
        reddit_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://reddit.com/r/aniripofficial"))
        )

        help_btn = QPushButton(" Help")
        help_btn.setIcon(QIcon(HELP_ICON_PATH))
        help_btn.setIconSize(icon_size)
        help_btn.setStyleSheet(btn_style)
        help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://raw.githubusercontent.com/NatsukiSubaruGH/anirip/refs/heads/main/help.txt")))

        for btn in (github_btn, reddit_btn, help_btn):
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)
        self.setFixedWidth(150)
        self.setStyleSheet("background-color: #E0F2F1;")


class MainContent(QWidget):
    def __init__(self, background_image_path):
        super().__init__()
        self.bg_pixmap = QPixmap(background_image_path)
        self.init_ui()

    def init_ui(self):
        self.setMinimumWidth(650)
        layout = QVBoxLayout()

        # Search bar + button
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter anime name...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1.5px solid #009688;
            }
        """)
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
            QPushButton:pressed {
                background-color: #004D40;
            }
        """)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Anime select combo hidden initially
        self.anime_select = QComboBox()
        self.anime_select.hide()
        self.anime_select.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QComboBox:hover {
                border: 1.5px solid #009688;
            }
        """)
        layout.addWidget(self.anime_select)

        # Controls in horizontal row: language, quality, episodes
        controls_layout = QHBoxLayout()

        label_style = "color: #444444; font-weight: 600;"

        self.lang_select = QComboBox()
        self.lang_select.addItems(["JP Sub", "Eng Dub"])
        self.lang_select.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QComboBox:hover {
                border: 1.5px solid #009688;
            }
        """)
        controls_layout.addWidget(QLabel("Language:"))
        controls_layout.itemAt(controls_layout.count()-1).widget().setStyleSheet(label_style)
        controls_layout.addWidget(self.lang_select)

        self.quality_select = QComboBox()
        self.quality_select.addItems(["1080p", "720p", "360p"])
        self.quality_select.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QComboBox:hover {
                border: 1.5px solid #009688;
            }
        """)
        controls_layout.addWidget(QLabel("Quality:"))
        controls_layout.itemAt(controls_layout.count()-1).widget().setStyleSheet(label_style)
        controls_layout.addWidget(self.quality_select)

        self.ep_input = QLineEdit()
        self.ep_input.setPlaceholderText("Episodes (all / range 1-12 / list 1,3,5)")
        self.ep_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1.5px solid #009688;
            }
        """)
        controls_layout.addWidget(QLabel("Episodes:"))
        controls_layout.itemAt(controls_layout.count()-1).widget().setStyleSheet(label_style)
        controls_layout.addWidget(self.ep_input)

        layout.addLayout(controls_layout)

        # Start button
        self.start_btn = QPushButton("Start Download")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
            QPushButton:pressed {
                background-color: #004D40;
            }
        """)
        layout.addWidget(self.start_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                text-align: center;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #009688;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                color: #333333;
                font-family: monospace;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # Signals
        self.search_btn.clicked.connect(self.perform_search)
        self.anime_select.currentIndexChanged.connect(self.anime_selected)
        self.start_btn.clicked.connect(self.start_download)

        self.anime_results = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg_pixmap)
        super().paintEvent(event)

    def log(self, message):
        self.log_text.append(message)

    def perform_search(self):
        q = self.search_bar.text().strip()
        if not q:
            QMessageBox.warning(self, "Input Error", "Please enter an anime name.")
            return
        self.log(f"Searching for '{q}' ...")
        results = se(q)
        if not results:
            QMessageBox.information(self, "No results", "No anime found.")
            self.anime_select.hide()
            return
        self.anime_results = results
        self.anime_select.clear()
        for r in results:
            self.anime_select.addItem(r["title"])
        self.anime_select.show()
        self.log(f"Found {len(results)} results.")

    def anime_selected(self, index):
        # no action needed here for now
        pass

    def parse_episodes(self, ep_text, max_ep):
        ep_text = ep_text.lower()
        if ep_text == "all":
            return list(range(1, max_ep + 1))
        if ep_text.startswith("range"):
            try:
                _, rng = ep_text.split(" ", 1)
                start, end = map(int, rng.split("-"))
                return [i for i in range(start, end + 1) if 1 <= i <= max_ep]
            except:
                return []
        if ep_text.startswith("list"):
            try:
                _, lst = ep_text.split(" ", 1)
                return [int(x) for x in lst.split(",") if x.strip().isdigit() and 1 <= int(x) <= max_ep]
            except:
                return []
        # fallback direct parse
        if "-" in ep_text:
            try:
                start, end = map(int, ep_text.split("-"))
                return [i for i in range(start, end + 1) if 1 <= i <= max_ep]
            except:
                return []
        if "," in ep_text:
            try:
                return [int(x) for x in ep_text.split(",") if x.strip().isdigit() and 1 <= int(x) <= max_ep]
            except:
                return []
        if ep_text.isdigit():
            n = int(ep_text)
            if 1 <= n <= max_ep:
                return [n]
        return []

    def start_download(self):
        if not self.anime_results:
            QMessageBox.warning(self, "Error", "Please search and select an anime first.")
            return
        idx = self.anime_select.currentIndex()
        if idx < 0 or idx >= len(self.anime_results):
            QMessageBox.warning(self, "Error", "Please select a valid anime.")
            return
        anime = self.anime_results[idx]

        lang = self.lang_select.currentText()
        quality = self.quality_select.currentText()
        episodes_text = self.ep_input.text().strip()
        max_ep = len(ep(anime["session"]))

        episodes = self.parse_episodes(episodes_text, max_ep)
        if not episodes:
            QMessageBox.warning(self, "Error", "Invalid or empty episode selection.")
            return

        output_dir = sf(anime["title"])
        os.makedirs(output_dir, exist_ok=True)

        self.log(f"Starting download: {anime['title']}")

        self.worker = DownloadWorker(
            anime["title"], anime["session"], episodes, lang, quality, output_dir
        )
        self.worker.progress.connect(self.log)
        self.worker.progress_percent.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.download_finished)
        self.worker.start()

    def download_finished(self, downloaded_eps):
        if downloaded_eps:
            self.log(f"Download finished: Episodes {', '.join(map(str, sorted(downloaded_eps)))}")
        else:
            self.log("No episodes downloaded.")


class AniRipMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniRip v1.0.0 - by Subaru Natsuki")
        self.resize(1000, 600)
        self.setWindowIcon(QIcon(WINDOW_ICON_PATH))

        layout = QHBoxLayout()
        self.side_menu = SideMenu()
        self.main_content = MainContent(WINDOW_ICON_PATH)

        layout.addWidget(self.side_menu)
        layout.addWidget(self.main_content)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #FAFAFA; color: #333333;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AniRipMainWindow()
    window.show()
    sys.exit(app.exec())
