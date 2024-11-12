class ToolCenterPoint(object):
    """
    ## Tool Center Point (TCP) class, for use with a UR5Robot.
    [Info]: A TCP, is a point in space deffined by 6 values for 3 dimentions.
    The 3 first numbers describes the location of the point in a 3D space (x, y, z)
    and the remaining 3 describes the orientation of the point in a 3D space (rx, ry, rz)

    #### Fields:
        - TCP:
            List of floating points of length 6, containing the TCP.

    #### Constructor:
        - __init__(self, [x, y, z, rx, ry, rz]):
    
    #### Functions:
        - Position(self):
            Returns the 3 first values determening the TCP location in a list.
        
        - Orientation(self):
            Returns the 3 last values determening the TCP orientation in a list.
    
    ##Examples
    ### Simple use:
        ```
        from ToolCenterPoint import ToolCenterPoint as TCP

        x, y, z = 0.5, 0, 0.25
        rx, ry, rz = 0.1, 0, 0.3
        
        point = TCP([x, y, z, rx, ry, rz])

        position = point.position()
        orientation = point.orientation()
        ```
    
    ### Used with ur_rtde:
        ```
        import rtde_control
        import rtde_recieve
        from ToolCenterPoint import ToolCenterPoint as TCP

        # Connect to a robot:
        ur5RobotsIpAdress = '172.31.1.144'
        control = rtde_control.RTDEControlInterface(ur5RobotsIpAdress)
        info = rtde_receive.RTDEReceiveInterface(ur5RobotsIpAdress)

        x, y, z = 0.5, 0, 0.25
        rx, ry, rz = 0.1, 0, 0.3
        oldPos = TCP(info.getActualTCPPose())
        newPos = TCP([x, y, z, rx, ry, rz])

        control.moveL(newPos.TCP)
    """

    TCP = None

    # Constructor:
    def __init__(self, TCP: 'list[float]') -> None:
        self.TCP = TCP

    # Methods:
    def position(self) -> 'list[float]':
        return self.TCP[:3]

    def orientation(self) -> 'list[float]':
        return self.TCP[3:]

    def __str__(self) -> str:
        TCP = self.TCP
        return f"[{TCP[0]}, {TCP[1]}, {TCP[2]}, {TCP[3]}, {TCP[4]}, {TCP[5]}]"