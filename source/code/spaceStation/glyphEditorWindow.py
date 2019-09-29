from AppKit import *
import vanilla
from mojo.roboFont import CurrentGlyph
from mojo.UI import StatusInteractivePopUpWindow, CurrentGlyphWindow
from .formulas import getFormula, setFormula, clearFormula, calculateFormula, getMetricValue, setMetricValue
from .tools import roundint


inSyncButtonColor = NSColor.blackColor()
outSyncButtonColor = NSColor.redColor()

escapeCharacter = "\x1B"


class GlyphEditorSpaceStationController(object):

    def __init__(self, glyph):
        self.w = StatusInteractivePopUpWindow((250, 0), centerInView=CurrentGlyphWindow().getGlyphView())

        metrics = dict(
            border=15,
            padding1=10,
            padding2=5,
            titleWidth=45,
            inputSpace=70, # border + title + padding
            killButtonWidth=20,
            navigateButtonWidth=30,
            fieldHeight=22,
        )
        rules = [
            # Left
            "H:|-border-[leftTitle(==titleWidth)]-padding1-[leftField]-border-|",
            "H:|-inputSpace-[leftButton]-padding2-[leftKillButton(==killButtonWidth)]-border-|",
            "V:|-border-[leftTitle(==fieldHeight)]",
            "V:|-border-[leftField(==fieldHeight)]",
            "V:[leftField]-padding2-[leftButton]",
            "V:[leftField]-padding2-[leftKillButton(==leftButton)]",

            # Right
            "H:|-border-[rightTitle(==titleWidth)]-padding1-[rightField]-border-|",
            "H:|-inputSpace-[rightButton]-padding2-[rightKillButton(==killButtonWidth)]-border-|",
            "V:[leftButton]-padding1-[rightTitle(==fieldHeight)]",
            "V:[leftButton]-padding1-[rightField(==fieldHeight)]",
            "V:[rightField]-padding2-[rightButton]",
            "V:[rightField]-padding2-[rightKillButton(==rightButton)]",

            # Width
            "H:|-border-[widthTitle(==titleWidth)]-padding1-[widthField]-border-|",
            "H:|-inputSpace-[widthButton]-padding2-[widthKillButton(==killButtonWidth)]-border-|",
            "V:[rightButton]-padding1-[widthTitle(==fieldHeight)]",
            "V:[rightButton]-padding1-[widthField(==fieldHeight)]",
            "V:[widthField]-padding2-[widthButton]",
            "V:[widthField]-padding2-[widthKillButton(==rightButton)]",

            # Bottom
            "H:|-inputSpace-[line]-border-|",
            "H:|-inputSpace-[previousGlyphButton(==navigateButtonWidth)]-padding2-[nextGlyphButton(==navigateButtonWidth)]-padding1-[doneButton(>=0)]-border-|",
            "V:[widthButton]-padding1-[line]",
            "V:[line]-padding1-[previousGlyphButton]-border-|",
            "V:[line]-padding1-[nextGlyphButton]-border-|",
            "V:[line]-padding1-[doneButton]-border-|",
        ]

        self.w.leftTitle = vanilla.TextBox("auto", "Left:", alignment="right")
        self.w.leftField = vanilla.EditText("auto", "", continuous=False, callback=self.fieldCallback)
        self.w.leftButton = vanilla.Button("auto", "", callback=self.buttonCallback)
        self.w.leftKillButton = vanilla.ImageButton("auto", imageNamed=NSImageNameStopProgressFreestandingTemplate, bordered=False, callback=self.buttonCallback)

        self.w.rightTitle = vanilla.TextBox("auto", "Right:", alignment="right")
        self.w.rightField = vanilla.EditText("auto", "", continuous=False, callback=self.fieldCallback)
        self.w.rightButton = vanilla.Button("auto", "", callback=self.buttonCallback)
        self.w.rightKillButton = vanilla.ImageButton("auto", imageNamed=NSImageNameStopProgressFreestandingTemplate, bordered=False, callback=self.buttonCallback)

        self.w.widthTitle = vanilla.TextBox("auto", "Width:", alignment="right")
        self.w.widthField = vanilla.EditText("auto", "", continuous=False, callback=self.fieldCallback)
        self.w.widthButton = vanilla.Button("auto", "", callback=self.buttonCallback)
        self.w.widthKillButton = vanilla.ImageButton("auto", imageNamed=NSImageNameStopProgressFreestandingTemplate, bordered=False, callback=self.buttonCallback)

        self.controlGroups = [
            dict(attr="leftMargin", field=self.w.leftField, button=self.w.leftButton, kill=self.w.leftKillButton),
            dict(attr="rightMargin", field=self.w.rightField, button=self.w.rightButton, kill=self.w.rightKillButton),
            dict(attr="width", field=self.w.widthField, button=self.w.widthButton, kill=self.w.widthKillButton),
        ]
        for group in self.controlGroups:
            field = group["field"]
            button = group["button"]
            button.getNSButton().setAlignment_(NSLeftTextAlignment)

        self.w.line = vanilla.HorizontalLine("auto")
        self.w.doneButton = vanilla.Button("auto", "Close", callback=self.doneCallback)
        self.w.doneButton.bind(escapeCharacter, [])
        self.w.previousGlyphButton = vanilla.Button("auto", "←", callback=self.previousGlyphCallback)
        self.w.previousGlyphButton.bind("[", ["command"])
        self.w.nextGlyphButton = vanilla.Button("auto", "→", callback=self.nextGlyphCallback)
        self.w.nextGlyphButton.bind("]", ["command"])

        self.w.addAutoPosSizeRules(rules, metrics)

        self.loadGlyph()

        self.w.open()

    def setFirstResponder(self, control):
        self.w.getNSWindow().makeFirstResponder_(control.getNSTextField())

    def _getControlGroup(self, sender):
        for group in self.controlGroups:
            field = group["field"]
            button = group["button"]
            kill = group["kill"]
            if sender == field:
                return group
            if sender == button:
                return group
            if sender == kill:
                return group

    def doneCallback(self, sender):
        self.w.close()

    # --------
    # Updaters
    # --------

    def loadGlyph(self):
        self._inGlyphLoad = True
        self.glyph = CurrentGlyph()
        if self.glyph.bounds is None:
            self.setFirstResponder(self.w.widthField)
        else:
            self.setFirstResponder(self.w.leftField)
        leftField = self.w.leftField.getNSTextField()
        rightField = self.w.rightField.getNSTextField()
        leftField.setNextKeyView_(rightField)
        rightField.setNextKeyView_(leftField)
        self._updateFields()
        self._updateButtons()
        self._inGlyphLoad = False

    def _updateFields(self):
        for group in self.controlGroups:
            attr = group["attr"]
            field = group["field"]
            if attr in ("leftMargin", "rightMargin") and self.glyph.bounds is None:
                value = ""
            else:
                value = getMetricValue(self.glyph, attr)
                value = roundint(value)
            field.set(value)

    def _updateButtons(self):
        for group in self.controlGroups:
            attr = group["attr"]
            button = group["button"]
            formula = getFormula(self.glyph, attr)
            if not formula:
                button.setTitle("")
                button.enable(False)
                continue
            calculatedValue = calculateFormula(self.glyph, formula, attr)
            value = getMetricValue(self.glyph, attr)
            if roundint(value) != roundint(calculatedValue):
                color = outSyncButtonColor
            else:
                color = inSyncButtonColor
            string = NSAttributedString.alloc().initWithString_attributes_(formula, {NSForegroundColorAttributeName : color})
            button.setTitle(string)
            button.enable(True)

    # ---------
    # Callbacks
    # ---------

    def fieldCallback(self, sender):
        if self._inGlyphLoad:
            return
        group = self._getControlGroup(sender)
        attr = group["attr"]
        field = group["field"]
        button = group["button"]
        value = field.get().strip()
        if value.startswith("="):
            formula = value[1:]
            if not formula:
                NSBeep()
                return
            value = calculateFormula(self.glyph, formula, attr)
            if value is None:
                NSBeep()
                return
            field.set(str(roundint(value)))
            setFormula(self.glyph, attr, formula)
        else:
            try:
                value = int(value)
            except:
                NSBeep()
                return
        self.glyph.prepareUndo("Spacing Change")
        setMetricValue(self.glyph, attr, value)
        self.glyph.performUndo()
        self._updateFields()
        self._updateButtons()

    def buttonCallback(self, sender):
        group = self._getControlGroup(sender)
        attr = group["attr"]
        field = group["field"]
        button = group["button"]
        kill = group["kill"]
        if sender == kill:
            clearFormula(self.glyph, attr)
        else:
            formula = button.getTitle()
            value = calculateFormula(self.glyph, formula, attr)
            if value is None:
                NSBeep()
                return
            self.glyph.prepareUndo("Spacing Change")
            setMetricValue(self.glyph, attr, value)
            self.glyph.performUndo()
        self._updateFields()
        self._updateButtons()

    def previousGlyphCallback(self, sender):
        CurrentGlyphWindow().getGlyphView().previousGlyph_()
        self.loadGlyph()

    def nextGlyphCallback(self, sender):
        CurrentGlyphWindow().getGlyphView().nextGlyph_()
        self.loadGlyph()

