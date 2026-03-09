class ToolCenterPoint(object):
    """
    ## Tool Center Point (TCP) class, for use with a UR5Robot.
    A TCP is a point in space defined by 6 values for 3 dimensions.
    The first 3 numbers describe the location (x, y, z)
    and the remaining 3 describe the orientation (rx, ry, rz).
    """

    def __init__(self, TCP: "list[float]") -> None:
        if TCP is None:
            raise ValueError("TCP cannot be None")
        if not isinstance(TCP, (list, tuple)):
            raise TypeError(
                f"TCP must be a list or tuple of 6 floats, got {type(TCP).__name__}"
            )
        if len(TCP) != 6:
            raise ValueError(f"TCP must have exactly 6 elements, got {len(TCP)}")
        for i, v in enumerate(TCP):
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"TCP element {i} must be numeric, got {type(v).__name__}"
                )
        self.TCP = list(TCP)  # Store a copy to avoid external mutation

    def position(self) -> "list[float]":
        """Returns [x, y, z]."""
        return self.TCP[:3]

    def orientation(self) -> "list[float]":
        """Returns [rx, ry, rz]."""
        return self.TCP[3:]

    def __getitem__(self, key):
        return self.TCP[key]

    def __setitem__(self, key, value):
        self.TCP[key] = value

    def __len__(self) -> int:
        return len(self.TCP)

    def __repr__(self) -> str:
        return f"TCP({self.TCP})"

    def __str__(self) -> str:
        return f"[{self.TCP[0]}, {self.TCP[1]}, {self.TCP[2]}, {self.TCP[3]}, {self.TCP[4]}, {self.TCP[5]}]"
