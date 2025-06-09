# MVP Instagram Bot for Client Demonstration

## Project Goal
This project is a Python-based MVP (Minimum Viable Product) designed to demonstrate basic Instagram automation capabilities to a client. The script controls a physical Android device connected via USB, automating actions like logging in, navigating to a user's profile, following them, liking posts, and commenting.

## Features
- Launches Instagram on a connected Android device.
- Logs into a specified Instagram account.
- Navigates to a target user's profile.
- Follows the target user.
- Likes the two most recent posts of the target user.
- Posts a random comment (from a predefined list) on the most recent post.
- Implements random delays between actions to simulate human behavior.
- Logs all major actions to `logfile.log` and the console.
- Captures screenshots at key moments (e.g., after login, after following) and saves them to the `screenshots/` directory.

## Technology Stack
- **Language:** Python 3
- **UI Automation:** `uiautomator2`
- **Device Control:** Android Debug Bridge (ADB)

## Project Structure
- `main.py`: The main executable script containing the bot's logic.
- `config.py`: Configuration file for Instagram credentials, target account(s), and comment templates.
- `requirements.txt`: Lists Python dependencies.
- `logfile.log`: Text file for logging bot actions.
- `screenshots/`: Directory where screenshots are saved.
- `README.md`: This documentation file.

## Prerequisites
1.  **Python 3:** Ensure Python 3.6 or higher is installed on your system.
2.  **ADB (Android Debug Bridge):**
    *   ADB must be installed and accessible from your command line.
    *   You can install it as part of the Android SDK Platform Tools.
3.  **Android Device:**
    *   A physical Android device (or an emulator).
    *   Developer Options enabled on the device.
    *   USB Debugging enabled within Developer Options.
    *   When connecting the device to your computer via USB, authorize the connection if prompted on the device.

## Setup Instructions
1.  **Clone the Repository:**
    ```bash
    # Replace with the actual repository URL
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
2.  **Install Dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Connect Android Device & Verify ADB:**
    *   Connect your Android device to your computer via USB.
    *   Ensure USB Debugging is enabled and authorized.
    *   Open your terminal or command prompt and verify the device is recognized by ADB:
        ```bash
        adb devices
        ```
        You should see your device listed. If not, troubleshoot your ADB setup and device connection. The `uiautomator2` library also includes a tool to help initialize the device:
        ```bash
        python -m uiautomator2 init
        ```
        This will install the necessary ATX agent on your device.

4.  **Update Configuration (`config.py`):**
    Open the `config.py` file and update the following variable with your actual Instagram password:
    ```python
    INSTAGRAM_PASSWORD = "ВВЕДІТЬ_ВАШ_ПАРОЛЬ_СЮДИ" # Replace this with your real password
    ```
    You can also change `INSTAGRAM_USERNAME`, `TARGET_ACCOUNTS`, and `COMMENT_TEMPLATES` if needed.

## How to Run the Script
Once all prerequisites and setup steps are completed:
1.  Ensure your Android device is connected and recognized by ADB.
2.  Make sure the Instagram app is installed on the device.
3.  Navigate to the project directory in your terminal.
4.  If you use a virtual environment, activate it.
5.  Run the main script:
    ```bash
    python main.py
    ```

## Expected Output
-   **Console Logs:** The script will print log messages to the console indicating its current actions.
-   **Log File (`logfile.log`):** All actions performed by the bot, along with timestamps, will be recorded in this file.
-   **Screenshots (`screenshots/` directory):** Screenshots will be saved in this directory at key moments, such as after a successful login, after following a user, after liking a post, and after commenting. These are named with a prefix and a timestamp (e.g., `login_successful_20231027_103045.png`).

## Important Notes & Disclaimers
-   **For Educational & Demonstration Purposes Only:** This bot is an MVP created for demonstrating UI automation capabilities.
-   **Instagram's Terms of Service:** Using automated scripts can be against Instagram's Terms of Service. Use responsibly and at your own risk. Frequent or aggressive automation can lead to account restrictions or bans.
-   **UI Selectors:** Instagram's app UI can change frequently, which may break the `uiautomator2` selectors used in this script (e.g., `resourceId`, `text`, `xpath`). If the script fails, these selectors in `main.py` are the most likely components that need updating.
-   **Device Performance:** The script's performance and reliability can be affected by the Android device's speed and the network connection.
