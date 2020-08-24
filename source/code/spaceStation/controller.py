from AppKit import NSBeep
from fontParts.world import CurrentGlyph, CurrentFont
from .glyphEditorWindow import GlyphEditorSpaceStationController
from .fontEditorWindow import FontEditorSpaceStationController

controllerIdentifier = "com.typesupply.SpaceStation"


class _SpaceStationController(object):

    identifier = controllerIdentifier

    def showGlyphEditorSpaceStation(self):
        glyph = CurrentGlyph()
        if glyph is not None:
            GlyphEditorSpaceStationController(glyph)
        else:
            NSBeep()

    def showFontEditorSpaceStation(self):
        font = CurrentFont()
        if font is not None:
            FontEditorSpaceStationController(font.defaultLayer)
        else:
            NSBeep()
