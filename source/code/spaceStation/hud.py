"""
- are the lines necessary?
- hide during preview
"""

import AppKit
import vanilla
import ezui
import merz
from mojo import subscriber

from .formulas import (
    getFormula,
    setFormula,
    clearFormula,
    calculateFormula,
    getMetricValue,
    setMetricValue
)
from .tools import roundint

extensionID = "com.typesupply.SpaceStation"
killImage = ezui.makeImage(symbolName="x.circle")

class SpaceStationHUDSubscriber(subscriber.Subscriber):

    debug = False

    def build(self):
        window = self.getGlyphEditor()

        self.backgroundColor = AppKit.NSColor.colorWithCalibratedWhite_alpha_(1, 0.9)
        self.hideColor = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0, 0)
        self.lineColor = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.8, 1)
        self.textColor = AppKit.NSColor.colorWithCalibratedWhite_alpha_(0.7, 1)
        self.invalidTextColor = AppKit.NSColor.redColor()

        configuration = AppKit.NSImageSymbolConfiguration.configurationWithPaletteColors_(
            [
                self.textColor
            ]
        )
        self.killImage = killImage.imageWithSymbolConfiguration_(configuration)

        subview = vanilla.Group((0, -75, 0, 50))
        subview.background = vanilla.Box(
            "auto",
            fillColor=self.backgroundColor,
            borderColor=self.hideColor,
            borderWidth=None,
            cornerRadius=10
        )
        subview.flex1 = vanilla.Group("auto")
        self.leftKill = subview.leftX = vanilla.ImageButton(
            "auto",
            imageObject=self.killImage,
            bordered=False,
            callback=self.leftKillCallback
        )
        self.leftText = subview.left = vanilla.SquareButton(
            "auto",
            "",
            callback=self.leftTextCallback
        )
        subview.line1 = vanilla.Box(
            "auto",
            borderColor=self.lineColor,
            fillColor=self.hideColor
        )
        self.widthKill = subview.widthX = vanilla.ImageButton(
            "auto",
            imageObject=self.killImage,
            bordered=False,
            callback=self.widthKillCallback
        )
        self.widthText = subview.width = vanilla.SquareButton(
            "auto",
            "",
            callback=self.widthTextCallback
        )
        subview.line2 = vanilla.Box(
            "auto",
            borderColor=self.lineColor,
            fillColor=self.hideColor
        )
        self.rightKill = subview.rightX = vanilla.ImageButton(
            "auto",
            imageObject=self.killImage,
            bordered=False,
            callback=self.rightKillCallback
        )
        self.rightText = subview.right = vanilla.SquareButton(
            "auto",
            "",
            callback=self.rightTextCallback
        )
        subview.flex2 = vanilla.Group("auto")

        buttons = [
            subview.left,
            subview.width,
            subview.right
        ]
        for button in buttons:
            button = button.getNSButton()
            button.setBordered_(False)
            button.setAlignment_(AppKit.NSTextAlignmentLeft)

        self.controlGroups = [
            dict(
                attr="leftMargin",
                text=self.leftText,
                kill=self.leftKill
            ),
            dict(
                attr="width",
                text=self.widthText,
                kill=self.widthKill
            ),
            dict(
                attr="rightMargin",
                text=self.rightText,
                kill=self.rightKill
            ),
        ]

        rules = [
            "H:|[flex1][background][flex2]|",
            "H:|"
                "[flex1]"
                "-padding-"
                "[left(==name)][leftX(==kill)]"
                "-spacing-"
                "[line1(==1)]"
                "-spacing-"
                "[width(==name)][widthX(==kill)]"
                "-spacing-"
                "[line2(==1)]"
                "-spacing-"
                "[right(==name)][rightX(==kill)]"
                "-padding-"
                "[flex2(==flex1)]"
              "|",
            "V:|[flex1]|",
            "V:|[background]|",
            "V:|-padding-[leftX]-padding-|",
            "V:|-padding-[left]-padding-|",
            "V:|-padding-[line1]-padding-|",
            "V:|-padding-[widthX]-padding-|",
            "V:|-padding-[width]-padding-|",
            "V:|-padding-[line2]-padding-|",
            "V:|-padding-[rightX]-padding-|",
            "V:|-padding-[right]-padding-|",
            "V:|[flex2]|"
        ]
        metrics = dict(
            padding=10,
            spacing=10,
            kill=20,
            name=100
        )
        subview.addAutoPosSizeRules(rules, metrics)

        window.addGlyphEditorSubview(
            subview,
            identifier=extensionID + ".GlyphEditorHUD",
            clear=True
        )

    def getGlyph(self):
        window = self.getGlyphEditor()
        glyph = window.getGlyph()
        return glyph

    # Events
    # ------

    def glyphEditorDidSetGlyph(self, info):
        self.updateControls()

    def glyphEditorGlyphDidChangeOutline(self, info):
        self.updateControls()

    def glyphEditorGlyphDidChangeMetrics(self, info):
        self.updateControls()

    # Updating
    # --------

    def updateControls(self):
        glyph = self.getGlyph()
        for group in self.controlGroups:
            attr = group["attr"]
            text = group["text"]
            kill = group["kill"]
            if glyph is None:
                text.show(False)
                kill.show(False)
                continue
            formula = getFormula(glyph, attr)
            if not formula:
                text.show(False)
                kill.show(False)
                continue
            calculatedValue = calculateFormula(glyph, formula, attr)
            value = getMetricValue(glyph, attr)
            if value is None:
                color = self.invalidTextColor
            elif roundint(value) != roundint(calculatedValue):
                color = self.invalidTextColor
            else:
                color = self.textColor
            string = AppKit.NSAttributedString.alloc().initWithString_attributes_(
                formula,
                {
                    AppKit.NSForegroundColorAttributeName : color
                }
            )
            text.setTitle(string)
            text.show(True)
            kill.show(True)

    # Callbacks
    # ---------

    def _reapplyFormulaCallback(self, sender, attr):
        glyph = self.getGlyph()
        formula = str(sender.getTitle())
        value = calculateFormula(glyph, formula, attr)
        glyph.prepareUndo("Spacing Change")
        setMetricValue(glyph, attr, value)
        glyph.performUndo()

    def _killFormulaCallback(self, attr):
        glyph = self.getGlyph()
        glyph.prepareUndo("Clear Spacing Formula")
        clearFormula(glyph, attr)
        glyph.performUndo()
        self.updateControls()

    def leftKillCallback(self, sender):
        self._killFormulaCallback("leftMargin")

    def leftTextCallback(self, sender):
        self._reapplyFormulaCallback(sender, "leftMargin")

    def rightKillCallback(self, sender):
        self._killFormulaCallback("rightMargin")

    def rightTextCallback(self, sender):
        self._reapplyFormulaCallback(sender, "rightMargin")

    def widthKillCallback(self, sender):
        self._killFormulaCallback("width")

    def widthTextCallback(self, sender):
        self._reapplyFormulaCallback(sender, "width")


# --
# Go
# --

def main():
    subscriber.registerGlyphEditorSubscriber(SpaceStationHUDSubscriber)

if __name__ == "__main__":
    SpaceStationHUDSubscriber.debug = True
    main()
