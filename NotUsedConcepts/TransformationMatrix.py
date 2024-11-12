import numpy as np

class TransformationMatrix:
    # DOCUMENTATION:
    # A transformation matrix is a 4 x 4 matrix describing the pose, or transformation of an object.
    # It consists of 3 matrixes/vectors:
    # 3 x 3 Orientation matrix.
    # 1 x 3 Position vector.
    # 4 x 1 Redundancy vector (always equal to [0, 0, 0, 1]).
    # 
    # Propperties:
    #  - Orientation: The 3 x 3 matrix representation of the pose orientation.
    #  - Position: The 1 x 3 vector representation of the pose position.
    #  - Redundancy: The 4 x 1 vector representation of the transformation matrixes' last line (Always [0, 0, 0, 1]).
    #  - Transformation: The full 4 x 4 matrix representation of the pose.
    # 
    # Constructors:
    #  - __init__(self): Creates an empty pbject.
    #  - __init__(self, transformationMatrix): Creates a new transformation matrix from an existing 4 x 4 matrix.
    #  - __init__(self, rotationMatrix, coordinateVector): Creates a new transformation matrix, 
    #    using a known orientationMatrix, coordinateVector and the redundancyVector.
    # 
    # Functions:
    # .
    
    Orientation = None
    Position = None
    Redundancy = [0, 0, 0, 1]
    Transformation = None

    def __init__(self):
        pass

    def __init__(self, transformationMatrix: "list[list[float]]"):
        self.Orientation = [transformationMatrix[0][0:2], transformationMatrix[1][0:2], transformationMatrix[2][0:2]]
        self.Position = [transformationMatrix[0][3], transformationMatrix[1][3], transformationMatrix[2][3]]
        self.Transformation = transformationMatrix

    def __init__(self, rotationMatrix: "list[list[float]]", coordinateVector: "list[float]"):
        self.Orientation = rotationMatrix
        self.Position = coordinateVector
        self.Transformation = [self.Orientation[0].append(self.Position[0]), self.Orientation[1].append(self.Position[1]), self.Orientation[2].append(self.Position[2]), self.Redundancy]
