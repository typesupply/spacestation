from AppKit import NSBeep
from fontParts.world import CurrentGlyph
from .glyphEditorWindow import GlyphEditorSpaceStationController

controllerIdentifier = "com.typesupply.SpaceStation"


class _SpaceStationController(object):

    identifier = controllerIdentifier

    def showGlyphEditorSpaceStation(self):
        glyph = CurrentGlyph()
        if glyph is not None:
            GlyphEditorSpaceStationController(glyph)
        else:
            NSBeep()
