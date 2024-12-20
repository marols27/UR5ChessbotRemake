![Python](https://img.shields.io/badge/python-3.8+-blue)

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

## Diagrams and charts
### Flowchart
The flowchart illustrates the user flow within the application, beginning at the home screen. It shows the steps a user can take, such as configuring the robot, setting up a game, and playing through different phases. Each stage of the game is represented, including move confirmation, turn logic, and game state transitions, culminating in a win, draw, or loss. This helps users and developers understand the application's sequential logic and user interactions.

```mermaid
flowchart TD
    run_app[Start Application] --> home_screen["Home Screen"]
    home_screen -->|Select Pose Configure| pose_configure["Pose Configure"]
    pose_configure -->|Calibrate Robot| calibration["Calibration Complete"]
    calibration -->|Press done| home_screen["Home Screen"]
    home_screen --> |Press Play game|choose_difficulty["Choose Difficulty"]
    choose_difficulty --> choose_color["Choose color"]
    choose_color -->|Press start| start{"Start"}
    
    start -->|Player is playing white| confirm_move["Press Confirm Move"]
    start -->|Player is playing black| robot_move[Robot Move]
    confirm_move -->|Check Game State| game_state{"Game State"}
    robot_move --> |Check Game State| game_state
    game_state --> |Players turn| confirm_move
    game_state --> |Robots turn| robot_move

    
    game_state -->|Win| end_game["Game Over: Win"]
    game_state -->|Draw| end_game["Game Over: Draw"]
    game_state -->|Loss| end_game["Game Over: Loss"]
    game_state -->|Resign| end_game["Game over"]
    
    end_game -->|Return to home screen| home_screen
```
### Domain diagram
The domain diagram provides an overview of the application's components and their relationships. It separates the system into three main parts:

1. Tkinter GUI: Includes screens like home, calibration, selection, and gameplay.

2. Backend: Contains the logic for robot control, chess operations, and configuration management.

3. app.py: Serves as the central controller, this is the file that is run calling creating an instanse of the gui

This diagram emphasizes modularity and how the application integrates diverse components into a cohesive workflow.


```mermaid
flowchart TD
    subgraph Tkinter_GUI["Tkinter GUI"]
        calibration_screen[Calibration Screen]
        home_screen[Home Screen]
        selection_screen[Selection Screen]
        game_screen[Game Screen]

        calibration_screen --> home_screen
        home_screen --> selection_screen
        selection_screen --> game_screen
        selection_screen --> home_screen
        game_screen --> home_screen
        home_screen --> calibration_screen
    end

    subgraph Backend
        PoseConfigure[Pose Configure]
        Settings[Settings]
        Game[Game]
        UR5Robot[UR5Robot]
        DGTBoard[DGTBoard]
        PythonChess[Python Chess]
        Board[Board]
        ToolCenterPoint[Tool Center Point]
        UR5Feature[UR5Feature]
        
        PoseConfigure -->|Writes to| ConfigFile[(Config File)]
        ConfigFile -->|Reads new values| Settings
        calibration_screen -->|Updates Variables| Settings
        calibration_screen --> PoseConfigure
        game_screen --> Settings
        Game --> DGTBoard
        Game --> Board
        Game --> PythonChess
        Game --> UR5Robot
        Board --> PythonChess
        Board --> UR5Feature
        Board --> ToolCenterPoint
        UR5Robot --> ToolCenterPoint
        UR5Robot --> UR5Feature
    end

    subgraph app.py[app.py]
        app
    end

    app-->|Initiates homescreen| home_screen

    game_screen -->|Creates & Uses| Game


```


### UML diagram
This is a more detailed diagram of the backend going into detail about the differen classes within the program
```mermaid
classDiagram
    class UR5Robot {
        + travelHeight: float
        + homePose: TCP
        + connectionIP: str
        + acceleration: float
        + speed: float
        + gripperSpeed: float
        + gripperForce: float
        + control: rtde_control.RTDEControlInterface(connectionIP)
        + info: rtde_receive.RTDEReceiveInterface(connectionIP)
        + getPose(): TCP
        + freeDrive(): void
        + goTo(pos: list[float]): void
        + grab(): void
        + drop(): void
        + home(): void
        + movePiece(fromPos: list[float], toPos: list[float], home=True): void
        + capturePiece(fromPos: list[float], toPos: list[float], capturePos: list[float]): void
        + enPassant(fromPos: list[float], toPos: list[float], targetPos: list[float]): void
        + castle(fromPosKing: list[float], toPosKing: list[float], fromPosRook: list[float], toPosRook: list[float]): void
        + promotion(fromPos: list[float], toPos: list[float]): void
        + capturePromotion(fromPos: list[float], toPos: list[float], capturePos: list[float]): void
    }
    class Game {
        + robot: UR5Robot
        + dgtBoard: DGTBoard
        + board: Board
        + engine: chess.engine.SimpleEngine
        + gameInfo: chess.pgn.Game
        + capturePos: TCP
        + timeout: chess.engine.limit
        + difficulty: int
        + color: bool
        + getPGN(): list[str]
        + playerMove(): void
        + runGameLoop(): void
        + playRobotMove(): void
    }

    class DGTBoard {
        + loop: event_loop
        + dgtConnection: asyncdgt.auto_connect(loop, port)
        + getCurrentBoard(): string
        + getCurrentBoardFen(): string
        + run(): void
    }

    class PoseConfigure {
        + connectionIP: str
        + fileName: str
        + firstTimeSetup(connectionIP: str, filename: str): void
        + recalibrate(point: Points, connectionIP: str, fileName='config.json'): void
        + freeMove(): void
        + start_teach_mode(): void
        + end_teach_mode(): void
        + calibrate_point(point: string): void
    }

    class Board {
        + startFen: str
        + feature: URSFeature
        + boardSize: float
        + squareSize: float
        + getSquareTCP(boardPos: str): TCP
        + getUCItoC(board: str): str
        + getMoveTCPbyUCI(self, uciMove: str, previousBoard: str): dict[str, TCP, TCP, TCP]
        + strBoardToMatrix(self, board: str): list[list[str]]
        + push(uci): void
        + getPGN(): str
    }

    class ToolCenterPoint {
        + TCP: list[float]
        + position(): list[float]
        + orientation(): list[float]
    }

    class URSFeature {
        + Origin: TCP
        + XAxis: TCP
        + XYPlane: TCP
        + xVector: ndarray
        + yVector: ndarray
        + zVector: ndarray
    }

    UR5Robot --> ToolCenterPoint
    UR5Robot --> URSFeature
    Board --> ToolCenterPoint
    Board --> URSFeature
    Game --> Board
    Game --> DGTBoard
    Game --> UR5Robot

```


## Current system capabilities
- [X] In app calibration of the robot
- [X] Select color and difficulty
- [X] Can do every type of move(Castling, en passant, capturing and normal moves)
- [X] Play a complete game of chess
- [X] View the movehistory of the current game
- [X] Resign a game
- [X] Win and lose

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
1. **Python Virtual Environment (Recommended)**  
   Activate the Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
3. **Install asyngdgt from github**
   ```bash
   pip install git+https://github.com/niklasf/python-asyncdgt

## Running application
1. **Activate viritual environment**
```bash
source venv/bin/activate
```
2. **Run the Application**
```bash
python3 app.py
```
## Future improvments
See issues!
