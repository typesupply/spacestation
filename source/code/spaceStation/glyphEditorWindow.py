from AppKit import *
import vanilla
from mojo.UI import StatusInteractivePopUpWindow, CurrentGlyphWindow
from .expressions import expressionLibKeyStub, calculateMetricsExpression, getAngledAttrIfNecessary
from .tools import roundint


inSyncButtonColor = NSColor.blackColor()
outSyncButtonColor = NSColor.redColor()

escapeCharacter = "\x1B"


class GlyphEditorSpaceStationController(object):

    def __init__(self, glyph):
        self.glyph = glyph

        self.w = StatusInteractivePopUpWindow((250, 239), centerInView=CurrentGlyphWindow().getGlyphView())

        margin = 15
        titleLeft = margin
        titleWidth = 45
        fieldLeft = titleLeft + titleWidth + 5
        fieldWidth = -margin
        buttonLeft = fieldLeft
        buttonWidth = -margin
        top = margin

        self.w.leftTitle = vanilla.TextBox(
            (titleLeft, top + 3, titleWidth, 17),
            "Left:",
            alignment="right"
        )
        self.w.leftField = vanilla.EditText(
            (fieldLeft, top, fieldWidth, 22),
            "",
            continuous=False,
            callback=self.fieldCallback
        )
        self.w.leftButton = vanilla.Button(
            (buttonLeft, top + 25, buttonWidth, 22),
            "",
            callback=self.buttonCallback
        )
        top += 60

        self.w.rightTitle = vanilla.TextBox(
            (titleLeft, top + 3, titleWidth, 17),
            "Right:",
            alignment="right"
        )
        self.w.rightField = vanilla.EditText(
            (fieldLeft, top, fieldWidth, 22),
            "",
            continuous=False,
            callback=self.fieldCallback
        )
        self.w.rightButton = vanilla.Button(
            (buttonLeft, top + 25, buttonWidth, 22),
            "",
            callback=self.buttonCallback
        )
        top += 60

        self.w.widthTitle = vanilla.TextBox(
            (titleLeft, top + 3, titleWidth, 17),
            "Width:",
            alignment="right"
        )
        self.w.widthField = vanilla.EditText(
            (fieldLeft, top, fieldWidth, 22),
            "",
            continuous=False,
            callback=self.fieldCallback
        )
        self.w.widthButton = vanilla.Button(
            (buttonLeft, top + 25, buttonWidth, 22),
            "",
            callback=self.buttonCallback
        )

        self.controlGroups = [
            dict(attr="leftMargin", field=self.w.leftField, button=self.w.leftButton),
            dict(attr="rightMargin", field=self.w.rightField, button=self.w.rightButton),
            dict(attr="width", field=self.w.widthField, button=self.w.widthButton),
        ]
        for group in self.controlGroups:
            field = group["field"]
            button = group["button"]
            button.getNSButton().setAlignment_(NSLeftTextAlignment)

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

        self.w.line = vanilla.HorizontalLine((buttonLeft, -47, buttonWidth, 1))
        self.w.doneButton = vanilla.Button(
            (buttonLeft, -37, buttonWidth, 22),
            "Close",
            callback=self.doneCallback
        )
        self.w.doneButton.bind(escapeCharacter, [])

        self.w.open()

    def setFirstResponder(self, control):
        self.w.getNSWindow().makeFirstResponder_(control.getNSTextField())

    def _getControlGroup(self, sender):
        for group in self.controlGroups:
            field = group["field"]
            button = group["button"]
            if sender == field:
                return group
            if sender == button:
                return group

    def doneCallback(self, sender):
        self.w.close()

    # --------
    # Updaters
    # --------

    def _updateFields(self):
        for group in self.controlGroups:
            attr = group["attr"]
            field = group["field"]
            if attr in ("leftMargin", "rightMargin") and self.glyph.bounds is None:
                value = ""
            else:
                attr = getAngledAttrIfNecessary(self.glyph.font, attr)
                value = getattr(self.glyph, attr)
                value = roundint(value)
            field.set(value)

    def _updateButtons(self):
        for group in self.controlGroups:
            attr = group["attr"]
            button = group["button"]
            expression = self.glyph.lib.get(expressionLibKeyStub + attr)
            if not expression:
                button.setTitle("")
                button.enable(False)
                return
            calculatedValue = calculateMetricsExpression(self.glyph, expression, attr)
            value = getattr(self.glyph, attr)
            if roundint(value) != roundint(calculatedValue):
                color = outSyncButtonColor
            else:
                color = inSyncButtonColor
            string = NSAttributedString.alloc().initWithString_attributes_(expression, {NSForegroundColorAttributeName : color})
            button.setTitle(string)
            button.enable(True)

    # ---------
    # Callbacks
    # ---------

    def fieldCallback(self, sender):
        group = self._getControlGroup(sender)
        attr = group["attr"]
        field = group["field"]
        button = group["button"]
        value = field.get().strip()
        if value.startswith("="):
            expression = value[1:]
            if not expression:
                NSBeep()
                return
            value = calculateMetricsExpression(self.glyph, expression, attr)
            if value is None:
                NSBeep()
                return
            field.set(str(roundint(value)))
            self.glyph.lib[expressionLibKeyStub + attr] = expression
        else:
            try:
                value = int(value)
            except:
                NSBeep()
                return
        self.glyph.prepareUndo("Spacing Change")
        attr = getAngledAttrIfNecessary(self.glyph.font, attr)
        setattr(self.glyph, attr, value)
        self.glyph.performUndo()
        self._updateFields()
        self._updateButtons()

    def buttonCallback(self, sender):
        group = self._getControlGroup(sender)
        attr = group["attr"]
        field = group["field"]
        button = group["button"]
        expression = button.getTitle()
        value = calculateMetricsExpression(self.glyph, expression, attr)
        if value is None:
            NSBeep()
            return
        self.glyph.prepareUndo("Spacing Change")
        attr = getAngledAttrIfNecessary(self.glyph.font, attr)
        setattr(self.glyph, attr, value)
        self.glyph.performUndo()
        self._updateFields()
        self._updateButtons()
