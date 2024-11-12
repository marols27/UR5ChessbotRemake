import asyncio
import asyncdgt
import threading

class DGTBoard():
    # CLASS DOCUMENTATION
    # A class for handling the conection of the physical DGT chess board, and it's streams.
    

    # FIELDS:
    # - loop: asyncronus loop that runns the dgtSocket handlers.
    # - dgtConnection: the asyncronus conection to the dgt board.


    # CONSTRUCTOR:
    # __init__():


    # METHODES:
    # getCurentBoard(): returns a string representation of the curent board in a 15 x 8 size, (15 because of spaces between each squares).

    def __init__(self, port: str = "/dev/ttyS0") -> None:
        #threading.Thread()
        self.loop = asyncio.new_event_loop()
        self.dgtConnection = asyncdgt.auto_connect(self.loop, [port])
    
    def getCurentBoard(self) -> str:
        strBoard = str(self.loop.run_until_complete(self.dgtConnection.get_board()))
        return strBoard
    
    def getCurentBoardFen(self) -> str:
        strBoard = str(self.loop.run_until_complete(self.dgtConnection.get_board())).split("\n")
        emptySpacesCounter = 0
        for i in range(len(strBoard)):
            strBoard[i] = strBoard[i].split(" ")
        fen = ""
        for y in range(len(strBoard)):
            for x in range(len(strBoard[y])):
                if strBoard[y][x] != ".":
                    if emptySpacesCounter > 0:
                        fen += str(emptySpacesCounter)
                        emptySpacesCounter = 0
                    fen += strBoard[y][x]
                else:
                    emptySpacesCounter += 1
                    if x == 7:
                        fen += str(emptySpacesCounter)
                        emptySpacesCounter = 0
            if y < 7:
                fen += "/"
        return fen
    
    def run(self):
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.dgtConnection.close()
            self.loop.close()