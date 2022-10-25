from AppKit import NSApp
from spaceStation.controller import _SpaceStationController
from spaceStation.hud import main

if __name__ == "__main__":
    NSApp().SpaceStationController = _SpaceStationController()
    main()