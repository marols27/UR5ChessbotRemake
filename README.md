![Python](https://img.shields.io/badge/python-3.12+-blue)

# UR5ChessbotRemake

![The hvl robotics chessrobot](/assets/images/demoimage.png "Image og setup")

## Introduction

The HVL Robotics Chess Robot is a student-developed project aimed at providing hands-on experience to students in automation and informatics. The project integrates various challenging tasks such as:

- Mapping the chessboard for accurate robot interaction
- Detecting changes on the board and responding appropriately
- Handling errors from the human opponent
- Integrating and using the Stockfish engine to determine strong chess moves
- Providing a user-friendly way to adjust settings from within the application
- Offering a graphical user interface (GUI) for calibration, difficulty and color selection, move confirmations, historical move review, and more

This robot has been showcased at HVL Robotics events to visitors, demonstrating the possibilities of combining robotics, software development, and AI-driven gameplay.

## Required Equipment

- **DGT Chessboard**: Ensures accurate piece detection and move validation. [View Product](https://digitalgametechnology.com/products/home-use-e-boards/usb-e-board-rosewood-in-gift-box)
- **UR5 Robot**: A robotic arm for physically moving the chess pieces. [View Product](https://www.universal-robots.com/no/produkter/ur5-robot/)
- **Touchscreen (Optional)**: Enhances user interaction and accessibility. [View Product](https://raspberrypi.dk/no/produkt/133-hdmi-touchscreen-display-med-case/?currency=NOK)
- **Computer**: Currently the main platform. (Testing on Raspberry Pi is planned for future iterations.)
- **Operating System**: Currently tested only on an Ubuntu Foxy virtual machine.[Read about it here](https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Debians.html)

## Changing settings

At the moment only configuration of the robot is possible to change from the GUI, the rest has to be manually changed in the Settings.py file.
Remember evaluate the safety of changes related to the robot, to high speeds could create danger for users, rule of thumb is to keep the robot moving under 250mm a second

## Installing Requirements

[uv](https://docs.astral.sh/uv/) is the recommended way to manage dependencies.

1. **Install uv** (if not already installed)

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Running on real hardware** — install the hardware extras (UR5 RTDE and serial support):

   ```bash
   uv sync --extra hardware
   ```

4. **Install asyncdgt** — this library is not on PyPI and must be installed manually from the DGT SDK:
   ```bash
   uv pip install git+https://github.com/niklasf/python-asyncdgt
   ```

## Running application

```bash
uv run app.py
```

## Future improvments

See issues!
