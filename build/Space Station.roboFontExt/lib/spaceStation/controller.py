from AppKit import NSBeep
from fontParts.world import CurrentGlyph
from booster.controller import BoosterController
from .glyphEditorWindow import GlyphEditorSpaceStationController

controllerIdentifier = "com.typesupply.SpaceStation"


class _SpaceStationController(BoosterController):

    identifier = controllerIdentifier

    def showGlyphEditorSpaceStation(self):
        glyph = CurrentGlyph()
        if glyph is not None:
            GlyphEditorSpaceStationController(glyph)
        else:
            NSBeep()
