import sys
import cv2
import numpy as np
import pyautogui
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMenuBar, QAction, 
    QDialog, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon
from pathlib import Path


class RenameDialog(QDialog):
    """ Custom Dialog for renaming recorded files """
    def __init__(self, current_filename, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename File")
        self.setGeometry(400, 300, 350, 120)
        self.setStyleSheet("background-color: black; color: white;")

        self.layout = QVBoxLayout()
        self.label = QLabel("Rename to:", self)
        self.label.setStyleSheet("color: white;")
        self.filename_input = QLineEdit(self)
        self.filename_input.setText(current_filename)  # Pre-fill with current name
        self.filename_input.setStyleSheet("background-color: gray; color: white;")
        self.rename_button = QPushButton("Rename")
        self.rename_button.setStyleSheet("background-color: darkgray; color: black;")

        self.rename_button.clicked.connect(self.accept)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.filename_input)
        self.layout.addWidget(self.rename_button)
        self.setLayout(self.layout)

    def get_filename(self):
        return self.filename_input.text().strip()


class AboutDialog(QDialog):
    """ About Dialog to show background image and info """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About BroadcastMe")
        self.setGeometry(400, 200, 600, 400)

        # Set background to black
        self.setStyleSheet("background-color: black;")

        # Create layout for the About Dialog
        layout = QVBoxLayout()

        # Add background image (PNG)
        self.image_label = QLabel(self)
        pixmap = QPixmap("background.png")  # Replace with your image file path
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)  # This was the source of the error

        # Add description text
        self.description_label = QLabel(
            "BroadcastMe - A Screen Recording Tool\n"
            "Version 1.0\n\n"
            "Developed by Zohan Haque",
            self
        )
        self.description_label.setStyleSheet("color: white; font-size: 16px; text-align: center;")
        layout.addWidget(self.image_label)
        layout.addWidget(self.description_label)

        self.setLayout(layout)


class BroadcastMe(QWidget):
    """ Main Screen Recorder UI """
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.screen_size = pyautogui.size()
        self.fps = 10
        self.out = None
        self.recorded_filename = "broadcastme_recorded.avi"
        self.save_directory = self.get_save_directory()  # Get the save directory

    def initUI(self):
        self.setWindowTitle("BroadcastMe - Screen Recorder")
        self.setGeometry(100, 100, 500, 200)
        self.setStyleSheet("background-color: black;")

        # Set the application icon to icon.png
        self.setWindowIcon(QIcon("icon.png"))

        # Menu Bar with White Background
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet("background-color: white; color: black;")
        file_menu = self.menu_bar.addMenu("File")
        help_menu = self.menu_bar.addMenu("Help")

        # Start Recording
        self.start_action = QAction("Start Recording", self)
        self.start_action.triggered.connect(self.start_recording)
        file_menu.addAction(self.start_action)

        # Stop Recording
        self.stop_action = QAction("Stop Recording", self)
        self.stop_action.triggered.connect(self.stop_recording)
        file_menu.addAction(self.stop_action)

        # Rename Option
        self.rename_action = QAction("Rename", self)
        self.rename_action.triggered.connect(self.open_rename_dialog)
        file_menu.addAction(self.rename_action)

        # Change Output Path Option
        self.change_output_action = QAction("Change Output Path", self)
        self.change_output_action.triggered.connect(self.change_output_path)
        file_menu.addAction(self.change_output_action)

        # Help Menu: About Option
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(self.about_action)

        # UI Elements
        self.label = QLabel("Ready to record. Use 'File' menu to control.", self)
        self.label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        # Layout
        layout = QVBoxLayout()
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Timer for capturing frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.record_frame)

    def get_save_directory(self):
        """ Gets the save directory (BroadcastME folder in Documents) """
        # Try to get the Documents path in a platform-independent way
        try:
            documents_folder = str(Path.home() / "Documents")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not determine the Documents folder: {e}")
            sys.exit(1)

        broadcast_me_folder = os.path.join(documents_folder, "BroadcastME")

        # Create the directory if it doesn't exist
        if not os.path.exists(broadcast_me_folder):
            try:
                os.makedirs(broadcast_me_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create BroadcastME folder: {e}")
                sys.exit(1)

        return broadcast_me_folder

    def start_recording(self):
        """ Starts screen recording """
        if not self.is_recording:
            self.is_recording = True
            self.label.setText("Recording...")

            # Set the full path for the recorded file
            self.recorded_filename = os.path.join(self.save_directory, "broadcastme_recorded.avi")
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.out = cv2.VideoWriter(self.recorded_filename, fourcc, self.fps, self.screen_size)
            
            self.timer.start(int(1000 / self.fps))

    def record_frame(self):
        """ Captures screen frames while recording """
        if self.is_recording:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.out.write(frame)

    def stop_recording(self):
        """ Stops recording """
        if self.is_recording:
            self.is_recording = False
            self.timer.stop()
            self.out.release()
            self.label.setText(f"Recording Stopped: {self.recorded_filename}")

    def open_rename_dialog(self):
        """ Opens the rename file window anytime, even if recording hasn't started """
        dialog = RenameDialog(self.recorded_filename, self)
        if dialog.exec_():
            new_filename = dialog.get_filename()

            if new_filename:
                if not new_filename.endswith(".avi"):
                    new_filename += ".avi"

                try:
                    new_filename_path = os.path.join(self.save_directory, new_filename)
                    os.rename(self.recorded_filename, new_filename_path)
                    self.recorded_filename = new_filename_path
                    self.label.setText(f"Filename set to: {new_filename}")
                except FileNotFoundError:
                    self.recorded_filename = new_filename
                    self.label.setText(f"New filename will be: {new_filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not rename file: {e}")
            else:
                QMessageBox.warning(self, "Warning", "Filename cannot be empty!")

    def change_output_path(self):
        """ Opens file dialog to change the output directory """
        new_directory = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.save_directory)

        if new_directory:
            broadcast_me_folder = os.path.join(new_directory, "BroadcastME")
            
            # Create the folder if it doesn't exist
            if not os.path.exists(broadcast_me_folder):
                os.makedirs(broadcast_me_folder)

            # Update the save directory to the new path
            self.save_directory = broadcast_me_folder
            self.recorded_filename = os.path.join(self.save_directory, "broadcastme_recorded.avi")
            self.label.setText(f"Output path changed to: {self.save_directory}")

    def show_about_dialog(self):
        """ Opens the About dialog to show the background image """
        dialog = AboutDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BroadcastMe()
    window.show()
    sys.exit(app.exec_())
