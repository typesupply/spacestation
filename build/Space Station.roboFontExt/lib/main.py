from AppKit import NSApp
from spaceStation.controller import _SpaceStationController

if __name__ == "__main__":
    NSApp().SpaceStationController = _SpaceStationController()
