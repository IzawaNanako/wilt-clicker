# Wilt Clicker

A highly customizable, Windows-exclusive autoclicker built with Python and CustomTkinter.

## Description

Wilt Clicker is an advanced automation tool designed to handle repetitive clicking tasks while offering features to simulate realistic inputs. Originally conceived with the fun idea of preventing users from "wilting" during tedious and repetitive computer tasks. It supports advanced features like CPS humanization and movement-based drop-offs to bypass basic macro detection or simply simulate natural behavior.

## Features

- **Advanced Humanization:** Add randomized CPS intervals to simulate natural human clicking.
- **Cursor Jittering:** Option to apply slight, randomized movements to the cursor while clicking.
- **Movement Drops:** Automatically lower the CPS rate when physical mouse movement is detected.
- **Click Limits:** Automatically stop clicking after a specific amount of time has passed or a certain number of clicks has been reached.
- **Coordinate Clicking:** Lock the autoclicker to a specific set of screen coordinates.
- **Global Master Switch:** Turn main clicker triggering off at will.
- **Hide Window:** Minimize the application to the system tray.
- **Customizable Hotkeys:** Bind feature toggles to any preferred key.

## Tech Stack

- **Language:** Python
- **GUI Framework:** CustomTkinter
- **Core Libraries:** keyboard

## Getting Started

You can run Wilt Clicker either by downloading the pre-compiled executable or by running the Python source code directly.

### Prerequisites

- **Operating System:** Windows
- **Environment:** Python 3.x (Only required if running from source).

### Installation & Execution

#### Option 1: Using the Executable (Recommended)

1. Navigate to the **Releases** section of this repository.
2. Download the latest `.exe` file.
3. Double-click to run the application.

> **Important Notes on the Executable:**
>
> - **Administrator Privileges:** Depending on the target application or game, you may need to right-click the `.exe` and select "Run as Administrator" for the simulated clicks to register properly.
> - **Antivirus Detection:** Because this tool intercepts keystrokes for hotkeys and simulates global mouse inputs, Windows Defender or other antivirus software may falsely flag the executable as suspicious. This is a common false positive for compiled Python automation tools.

#### Option 2: Running from Source

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/IzawaNanako/wilt-clicker.git
   cd wilt-clicker
   ```

2. Install the required dependencies:

   ```bash
   pip install .
   ```

3. Run the main application file:

   ```bash
   python src/main.py
   ```

### Building the Executable

If you wish to compile the executable yourself from the source code, you can do so using PyInstaller and the provided specification file.

1. Ensure PyInstaller is installed:

   ```bash
   pip install pyinstaller
   ```

2. Run the following command in the root directory:

   ```bash
   pyinstaller WiltClicker.spec --clean
   ```

The compiled .exe will be located in the generated dist/ folder.

### License

This project is licensed under the GPL-3.0 License - see [LICENSE](/LICENSE) for details.
