from AppKit import *
import vanilla

escapeCharacter = "$"

class GlyphEditorSpaceStationController(object):

    def __init__(self):
        self.glyph = CurrentGlyph()

        self.w = vanilla.Window((300, 0), minSize=(100, 100))

        metrics = dict(
            border=15,
            padding1=10,
            padding2=5,
            titleWidth=45,
            inputSpace=70, # border + title + padding
            killButtonWidth=20,
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
            "H:|-inputSpace-[doneButton]-border-|",
            "V:[widthButton]-padding1-[line]-padding1-[doneButton]-border-|",
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
            dict(attr="leftMargin", field=self.w.leftField, button=self.w.leftButton),
            dict(attr="rightMargin", field=self.w.rightField, button=self.w.rightButton),
            dict(attr="width", field=self.w.widthField, button=self.w.widthButton),
        ]
        for group in self.controlGroups:
            field = group["field"]
            button = group["button"]
            button.getNSButton().setAlignment_(NSLeftTextAlignment)

        # if self.glyph.bounds is None:
        #     self.setFirstResponder(self.w.widthField)
        # else:
        #     self.setFirstResponder(self.w.leftField)
        # leftField = self.w.leftField.getNSTextField()
        # rightField = self.w.rightField.getNSTextField()
        # leftField.setNextKeyView_(rightField)
        # rightField.setNextKeyView_(leftField)

        self.w.line = vanilla.HorizontalLine("auto")
        self.w.doneButton = vanilla.Button("auto", "Close", callback=self.doneCallback)
        self.w.doneButton.bind(escapeCharacter, [])

        self.w.addAutoPosSizeRules(rules, metrics)

        self.w.open()

    def fieldCallback(self, sender):
        pass

    def buttonCallback(self, sender):
        pass

    def doneCallback(self, sender):
        pass

GlyphEditorSpaceStationController()