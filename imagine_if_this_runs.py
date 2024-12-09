import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QLineEdit, QTextEdit, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QPalette

# my face when it happened: 💀

# for context: i told deepseek to rewrite my whole app in PyQt

def float_to_rgb(r, g, b, a=1.0):
    return int(r * 255), int(g * 255), int(b * 255), int(a * 255)

class RoundedButton(QPushButton):
    def __init__(self, text, normal_color, pressed_color):
        super().__init__(text)
        self.normal_color = normal_color
        self.pressed_color = pressed_color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba{self.normal_color};
                border-radius: 25px;
                padding: 10px;
                color: white;
            }}
            QPushButton:pressed {{
                background-color: rgba{self.pressed_color};
            }}
        """)

class RoundedLabel(QLabel):
    def __init__(self, text, background_color):
        super().__init__(text)
        self.background_color = background_color
        self.setWordWrap(True)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: rgba{self.background_color};
                border-radius: 30px;
                padding: 20px;
                color: white;
            }}
        """)

class BotResponseThread(QThread):
    response_ready = pyqtSignal(str)

    @staticmethod
    def _generate_message():
        return "I received your message: Hello, Bot!"

    def run(self):
        # Simulate bot response generation
        response = self._generate_message()
        self.response_ready.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Chat Bot")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.vertical_layout = QVBoxLayout(self.central_widget)

        # Top Layout
        self.top_layout = QHBoxLayout()
        self.toggle_sidebar_button = RoundedButton("Toggle Sidebar", float_to_rgb(0.2, 0.6, 1), float_to_rgb(0.8, 0.2, 0.2))
        self.toggle_sidebar_button.clicked.connect(self.toggle_sidebar)
        self.top_layout.addWidget(self.toggle_sidebar_button)
        self.top_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.label = QLabel("Conversation_1")
        self.top_layout.addWidget(self.label)
        self.top_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.new_chat_button = RoundedButton("New Chat", float_to_rgb(0.2, 0.6, 1), float_to_rgb(0.8, 0.2, 0.2))
        self.top_layout.addWidget(self.new_chat_button)
        self.vertical_layout.addLayout(self.top_layout)

        # Main Layout
        self.main_layout = QHBoxLayout()
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet(f"background-color: rgba{float_to_rgb(0.09, 0.09, 0.09)};")
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # Scrollable chat items
        self.scroll_sidebar = QScrollArea()
        self.scroll_sidebar.setWidgetResizable(True)
        self.chats_widget = QWidget()
        self.chats_layout = QVBoxLayout(self.chats_widget)
        for i in range(12):
            button = RoundedButton(f"Chat {i+2}", float_to_rgb(0.2, 0.6, 1), float_to_rgb(0.8, 0.2, 0.2))
            self.chats_layout.addWidget(button)
        self.scroll_sidebar.setWidget(self.chats_widget)
        self.sidebar_layout.addWidget(self.scroll_sidebar)

        # Profile Settings button
        self.profile_settings_button = RoundedButton("Profile Settings", float_to_rgb(0.2, 0.6, 1), float_to_rgb(0.8, 0.2, 0.2))
        self.sidebar_layout.addWidget(self.profile_settings_button)
        self.main_layout.addWidget(self.sidebar)

        # Main Chat Area
        self.main_chat_widget = QWidget()
        self.main_chat_layout = QVBoxLayout(self.main_chat_widget)

        # Scrollable chat log
        self.scroll_chat_log = QScrollArea()
        self.scroll_chat_log.setWidgetResizable(True)
        self.chat_log_widget = QWidget()
        self.chat_log_layout = QVBoxLayout(self.chat_log_widget)
        self.scroll_chat_log.setWidget(self.chat_log_widget)
        self.main_chat_layout.addWidget(self.scroll_chat_log)

        # Input Layout
        self.input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setStyleSheet(f"background-color: rgba{float_to_rgb(0.15, 0.15, 0.15)}; color: white;")
        self.input_box.returnPressed.connect(self.send_message)
        self.send_button = RoundedButton("Send", float_to_rgb(0.25, 0.25, 0.25), float_to_rgb(0.35, 0.35, 0.35))
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.input_box)
        self.input_layout.addWidget(self.send_button)
        self.main_chat_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.main_chat_widget)
        self.vertical_layout.addLayout(self.main_layout)

        self.sidebar_visible = True

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.hide()
            self.toggle_sidebar_button.setText("Open Sidebar")
        else:
            self.sidebar.show()
            self.toggle_sidebar_button.setText("Close Sidebar")
        self.sidebar_visible = not self.sidebar_visible

    def send_message(self):
        user_message = self.input_box.text().strip()
        if user_message:
            self.add_message(f"{user_message}", is_user_message=True)
            self.input_box.clear()
            self.send_button.setText("Stop")
            self.input_box.setDisabled(True)
            self.bot_thread = BotResponseThread()
            self.bot_thread.response_ready.connect(self.update_bot_response)
            self.bot_thread.start()

    def add_message(self, text, is_user_message=False):
        label = RoundedLabel(text, float_to_rgb(0.25, 0.25, 0.25) if is_user_message else float_to_rgb(0.15, 0.15, 0.15))
        if is_user_message:
            label.setAlignment(Qt.AlignRight)
        else:
            label.setAlignment(Qt.AlignLeft)
        self.chat_log_layout.addWidget(label)
        self.scroll_chat_log.verticalScrollBar().setValue(self.scroll_chat_log.verticalScrollBar().maximum())

    def update_bot_response(self, response):
        self.add_message(response, is_user_message=False)
        self.send_button.setText("Send")
        self.input_box.setDisabled(False)
        self.bot_thread.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())