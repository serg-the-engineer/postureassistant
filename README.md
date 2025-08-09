# Posture Assistant

**Posture Assistant** is a desktop application that helps you maintain a good posture while working at your computer. Using your webcam, it analyzes your position in real-time and sends notifications if you've been sitting incorrectly for an extended period.

The posture analysis is simple, based on a subjective observation: when sitting straight, the head is positioned higher than in any other slouching pose. This method works well with a static monitor position.

---

## ✨ Key Features

*   **Real-time Monitoring:** Tracks your head position using a webcam at a low FPS to conserve resources.
*   **Smart Notifications:** The app will only send a desktop notification if you've been sitting incorrectly for a prolonged time.
*   **Statistics:** View your daily statistics in a pie chart to see how long you've maintained a correct posture.
*   **Background Operation:** The application minimizes to the system tray and stays out of your way.

---

## 🚀 Installation

You can install Posture Assistant in two ways: by downloading the ready-to-use program or by running it from the source code.

### 1. For Users (Recommended Method)

This is the easiest way to get started.

Go to the project's **[Releases](https://github.com/serg-the-engineer/postureassistant/releases)** page.

#### **Windows** (In progress)
*   Download the `PostureAssistant-Setup.exe` file.
*   Run the installer and follow the on-screen instructions.
*   After installation, find the Posture Assistant shortcut in the Start Menu or on your desktop.

#### **macOS**
*   Download the `PostureAssistant.dmg` file.
*   Open the `.dmg` file and drag the `PostureAssistant` icon into your `Applications` folder.
*   On the first launch, you may need to allow the application from an unidentified developer in `System Settings` -> `Privacy & Security`.

---

### 2. For Developers (From Source Code)

This method is suitable if you want to modify the code or run it in your development environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/serg-the-engineer/postureassistant.git
    cd postureassistant
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    # For Windows
    pip install PyQt6 opencv-python matplotlib numpy pygrabber --pre

    # For macOS
    pip install PyQt6 opencv-python matplotlib numpy pyobjc-framework-AVFoundation
    ```

4.  **Run the application:**
    ```bash
    python -m src
    ```

---

## 🛠️ How to Use

1.  **Launch the application.**
2.  **Select your camera.** If you have multiple cameras, choose the desired one from the dropdown list.
3.  **Sit up straight** and click the **"Calibrate"** button. The app will save this position as the correct reference.
4.  Click the **"Start"** button. Monitoring will begin. The rectangle around your face will be green for correct posture and red for incorrect.
5.  **View Statistics:** Click the **"Statistics"** button to see a report for the current day.
6.  **Background Mode:** You can close the window, and the application will minimize to the system tray and continue running. Click the tray icon to bring the window back.

---

## 💻 Tech Stack

*   **Language:** Python 3
*   **GUI:** PyQt6
*   **Computer Vision:** OpenCV
*   **Charts:** Matplotlib
*   **Database:** SQLite
*   **Packaging:** PyInstaller

---

## ⚙️ How It Works

The application uses Haar Cascades from the OpenCV library to detect a face in the video stream. During calibration, it records the vertical coordinate (Y) of the center of the face. While monitoring, it compares the current Y-coordinate with the reference one. If the deviation exceeds a set threshold, the posture is considered incorrect. Data on the time spent in each state is saved to a local SQLite database for later analysis.

---

## 📄 License

This project is distributed under the MIT License.