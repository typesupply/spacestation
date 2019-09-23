from AppKit import NSApp

class SpaceStationError(Exception): pass

def SpaceStationController():
    return NSApp().SpaceStationController