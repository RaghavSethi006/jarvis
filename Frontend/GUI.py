from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit,
    QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QMouseEvent
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("AssistantName")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicDirPath = os.path.join(current_dir, "Frontend", "Graphics")

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query: str):
    new_query = query.strip().lower()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ["?", ".", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ["?", ".", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicrophoneStatus(command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding="utf-8") as file:
        file.write(command)

def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "False"

def SetAssistantStatus(status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(status)

SetAssistantStatus("Speaking...")

def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Offline"

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicDirectoryPath(Filename):
    return os.path.join(GraphicDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(text):
    with open(os.path.join(TempDirPath, "Responses.data"), 'w', encoding="utf-8") as file:
        file.write(text)

class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toggled = True  # Fixed typo: Changed 'Maker' to 'toggled'
        self.load_icon(GraphicDirectoryPath("Mic_on.png"))

    def mousePressEvent(self, ev: QMouseEvent | None):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            self.handle_icon_click()
        super().mousePressEvent(ev)

    def handle_icon_click(self):
        self.toggle_icon()

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path).scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(pixmap)

    def toggle_icon(self):
        if self.toggled:
            self.load_icon(GraphicDirectoryPath("voice.png"))
            MicButtonInitialized()
        else:
            self.load_icon(GraphicDirectoryPath("mic.png"))
            MicButtonClosed()
        self.toggled = not self.toggled

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet('background-color: black;')
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        text_color_text = QTextCharFormat()
        text_color_text.setForeground(QColor(Qt.GlobalColor.blue))
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicDirectoryPath("jarvis.gif"))
        movie.setScaledSize(QSize(400, 300))
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignRight or Qt.AlignmentFlag.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(self.label)
        layout.addWidget(self.gif_label)
        layout.setSpacing(-10)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as file:
                messages = file.read()
                if messages.strip() and old_chat_message != messages:
                    self.addMessage(messages, color="white")
                    old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.primaryScreen()
        screen_size = desktop.size() if desktop else QSize(1920, 1080)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicDirectoryPath("jarvis.gif"))
        gif_label.setMovie(movie)
        movie.setScaledSize(QSize(screen_size.width()//2 , int((screen_size.width()//2) / 4 * 3)))
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie.start()

        self.icon_label = ClickableLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedSize(screen_size)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        desktop = QApplication.primaryScreen()
        screen_size= desktop.size() if desktop else QSize(1920, 1080)
        self.setFixedSize(screen_size)
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        title_label = QLabel(f" {str(Assistantname).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white; padding: 5px;")
        layout.addWidget(title_label)
        layout.addStretch(1)

        def create_button(text, icon_path, callback):
            btn = QPushButton(text)
            btn.setIcon(QIcon(icon_path))
            btn.setStyleSheet("height:40px; background-color:white; color:black; border:none; padding:5px 10px;")
            btn.clicked.connect(callback)
            return btn

        layout.addWidget(create_button(" Home", GraphicDirectoryPath("Home.png"), lambda: self.stacked_widget.setCurrentIndex(0)))
        layout.addWidget(create_button(" Chat", GraphicDirectoryPath("Chats.png"), lambda: self.stacked_widget.setCurrentIndex(1)))

        self.maximize_button = create_button("", GraphicDirectoryPath("Maximize.png"), self.maximizeWindow)
        self.restore_icon = QIcon(GraphicDirectoryPath("Restore.png"))

        layout.addWidget(create_button("", GraphicDirectoryPath("Minimize2.png"), self.minimizeWindow))
        layout.addWidget(self.maximize_button)
        layout.addWidget(create_button("", GraphicDirectoryPath("Close.png"), self.closeWindow))

        self.draggable = True
        self.offset = None

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

    def minimizeWindow(self):
        window = self.window()
        if window:
            window.showMinimized()

    def maximizeWindow(self):
        window = self.window()
        if window:
            if window.isMaximized():
                window.showNormal()
                self.maximize_button.setIcon(QIcon(GraphicDirectoryPath("Maximize.png")))
            else:
                window.showMaximized()
                self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        window = self.window()
        if window:
            window.close()

    def mousePressEvent(self, a0: QMouseEvent | None):
        if self.draggable and a0 is not None and a0.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window:
                self.offset = a0.globalPos() - window.frameGeometry().topLeft()

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if self.draggable and self.offset is not None and a0 is not None and (a0.buttons() & Qt.MouseButton.LeftButton) != 0:
            window = self.window()
            if window:
                window.move(a0.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.primaryScreen()
        screen_size = desktop.size() if desktop else QSize(1920, 1080)
        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        self.setStyleSheet("background-color: black;")

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()