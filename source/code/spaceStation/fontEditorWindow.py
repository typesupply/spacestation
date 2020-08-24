import os
import AppKit
import vanilla
from mojo.UI import CurrentFontWindow
from spaceStation import formulas
from spaceStation import auto
from spaceStation import tools

class FontEditorSpaceStationController(object):

    def __init__(self, layer):
        self.layer = layer
        self.font = layer.font

        self.w = vanilla.Sheet(
            (946, 500),
            minSize=(946, 500),
            maxSize=(946, 50000),
            parentWindow=CurrentFontWindow().w
        )

        data = [
            self.getDataForGlyphName(glyphName)
            for glyphName in self.font.glyphOrder
        ]
        columnDescriptions = [
            dict(
                key="name",
                title="Name",
                editable=False
            ),
            dict(
                key="left",
                title="Left",
                editable=True
            ),
            dict(
                key="right",
                title="Right",
                editable=True
            ),
            dict(
                key="width",
                title="Width",
                editable=True
            )
        ]
        self.w.list = vanilla.List(
            "auto",
            data,
            columnDescriptions=columnDescriptions,
            drawFocusRing=False
        )
        self.w.updateAllButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameRefreshTemplate,
            bordered=False,
            callback=self.updateButtonCallback
        )
        self.w.clearAllButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameStopProgressTemplate,
            bordered=False,
            callback=self.clearButtonCallback
        )

        self.w.updateLeftButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameRefreshTemplate,
            bordered=False,
            callback=self.updateButtonCallback
        )
        self.w.clearLeftButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameStopProgressTemplate,
            bordered=False,
            callback=self.clearButtonCallback
        )

        self.w.updateRightButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameRefreshTemplate,
            bordered=False,
            callback=self.updateButtonCallback
        )
        self.w.clearRightButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameStopProgressTemplate,
            bordered=False,
            callback=self.clearButtonCallback
        )

        self.w.updateWidthButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameRefreshTemplate,
            bordered=False,
            callback=self.updateButtonCallback
        )
        self.w.clearWidthButton = vanilla.ImageButton(
            "auto",
            imageNamed=AppKit.NSImageNameStopProgressTemplate,
            bordered=False,
            callback=self.clearButtonCallback
        )

        self.w.importButton = vanilla.Button(
            "auto",
            "Import",
            callback=self.importButtonCallback
        )
        self.w.exportButton = vanilla.Button(
            "auto",
            "Export",
            callback=self.exportButtonCallback
        )
        self.w.closeButton = vanilla.Button(
            "auto",
            "Close",
            callback=self.closeButtonCallback
        )

        metrics = dict(
            margin=15,
            spacing=10,
            padding=5,
            imageButton=20,
            button=100,
            column=225,
            column1=15,
            column2=240,
            column3=465,
            column4=690
        )
        rules = [
            "H:|-column1-[updateAllButton(==imageButton)]-padding-[clearAllButton(==imageButton)]",
            "H:|-column2-[updateLeftButton(==imageButton)]-padding-[clearLeftButton(==imageButton)]",
            "H:|-column3-[updateRightButton(==imageButton)]-padding-[clearRightButton(==imageButton)]",
            "H:|-column4-[updateWidthButton(==imageButton)]-padding-[clearWidthButton(==imageButton)]",
            "H:|-margin-[list]-margin-|",
            "H:|-margin-[importButton(==button)]-spacing-[exportButton(==button)]",
            "H:[closeButton(==button)]-margin-|",
            "V:|"
                "-margin-"
                "[updateAllButton(==imageButton)]"
                "-padding-"
                "[list]"
                "-spacing-"
                "[importButton]"
                "-margin-"
            "|",
            "V:|"
                "-margin-"
                "[clearAllButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[updateLeftButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[clearLeftButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[updateRightButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[clearRightButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[updateWidthButton(==imageButton)]",
            "V:|"
                "-margin-"
                "[clearWidthButton(==imageButton)]",
            "V:"
                "[list]"
                "-spacing-"
                "[exportButton]",
            "V:"
                "[list]"
                "-spacing-"
                "[closeButton]",
        ]

        self.w.addAutoPosSizeRules(rules, metrics)
        self.w.open()

    def closeButtonCallback(self, sender):
        self.w.close()

    def updateAllData(self):
        for container in self.w.list:
            self.getDataForGlyphName(container["name"], container)

    def getDataForGlyphName(self, glyphName, container=None):
        if container is None:
            container = dict(
                name=glyphName,
                left=None,
                right=None,
                width=None
            )
        glyph = self.layer[glyphName]
        container["left"] = visualizeFormula(
            glyph,
            "leftMargin",
            formulas.getFormula(glyph, "leftMargin")
        )
        container["right"] = visualizeFormula(
            glyph,
            "rightMargin",
            formulas.getFormula(glyph, "rightMargin")
        )
        container["width"] = visualizeFormula(
            glyph,
            "width",
            formulas.getFormula(glyph, "width")
        )
        for k, v in container.items():
            if v is None:
                container[k] = ""
        return container

    # ------------
    # Update/Clear
    # ------------

    def updateButtonCallback(self, sender):
        attrMap = {
            self.w.updateAllButton : None,
            self.w.updateLeftButton : "leftMargin",
            self.w.updateRightButton : "rightMargin",
            self.w.updateWidthButton : "width"
        }
        attr = attrMap[sender]
        glyphNames = [self.w.list[i]["name"] for i in self.w.list.getSelection()]
        auto.applyFormulasInLayer(
            self.layer,
            onlyGlyphNames=glyphNames,
            onlyAttr=attr
        )
        self.updateAllData()

    def clearButtonCallback(self, sender):
        attrMap = {
            self.w.clearAllButton : None,
            self.w.clearLeftButton : "leftMargin",
            self.w.clearRightButton : "rightMargin",
            self.w.clearWidthButton : "width"
        }
        attr = attrMap[sender]
        glyphNames = [self.w.list[i]["name"] for i in self.w.list.getSelection()]
        for glyphName in glyphNames:
            glyph = self.layer[glyphName]
            if attr is None:
                formulas.clearFormula(glyph, "leftMargin")
                formulas.clearFormula(glyph, "rightMargin")
                formulas.clearFormula(glyph, "width")
            else:
                formulas.clearFormula(glyph, attr)
        self.updateAllData()

    # -------------
    # Import/Export
    # -------------

    def importButtonCallback(self, sender):
        vanilla.dialogs.getFile(
            fileTypes=["spacestation"],
            resultCallback=self._importCallback,
            parentWindow=self.w
        )

    def _importCallback(self, path):
        if not path:
            return
        for glyph in layer:
            formulas.clearFormula(glyph, "leftMargin")
            formulas.clearFormula(glyph, "rightMargin")
            formulas.clearFormula(glyph, "width")
        path = path[0]
        f = open(path, "r")
        text = f.read()
        f.close()
        tools.readFormulasFromString(text, self.layer)
        self.updateAllData()

    def exportButtonCallback(self, sender):
        directory = os.path.dirname(font.path)
        fileName = os.path.splitext(os.path.basename(font.path))[0] + ".spacestation"
        vanilla.dialogs.putFile(
            resultCallback=self._exportCallback,
            parentWindow=self.w,
            directory=directory,
            fileName=fileName
        )

    def _exportCallback(self, path):
        if not path:
            return
        text = tools.writeFormulasToString(self.layer)
        f = open(path, "w")
        f.write(text)
        f.close()


red = AppKit.NSColor.redColor()

def visualizeFormula(glyph, attr, formula):
    if not formula:
        return formula
    calculatedValue = formulas.calculateFormula(glyph, formula, attr)
    value = formulas.getMetricValue(glyph, attr)
    if tools.roundint(value) != tools.roundint(calculatedValue):
        formula = AppKit.NSAttributedString.alloc().initWithString_attributes_(
                formula,
                {AppKit.NSForegroundColorAttributeName : red}
            )
    return formula
