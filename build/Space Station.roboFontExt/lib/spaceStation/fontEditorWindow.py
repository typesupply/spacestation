import os
import fnmatch
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
            [],
            columnDescriptions=columnDescriptions,
            drawFocusRing=False,
            editCallback=self.listEditCallback
        )

        self.w.filterSearchBox = vanilla.SearchBox(
            "auto",
            callback=self.populateList
        )
        self.w.prioritizeProblemsCheckBox = vanilla.CheckBox(
            "auto",
            "Prioritize Problems",
            value=True,
            callback=self.populateList
        )

        self.w.line = vanilla.HorizontalLine("auto")

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
            "H:|-margin-[filterSearchBox(==215)]-spacing-[prioritizeProblemsCheckBox]",
            "H:|-margin-[line]-margin-|",
            "H:|-column1-[updateAllButton(==imageButton)]-padding-[clearAllButton(==imageButton)]",
            "H:|-column2-[updateLeftButton(==imageButton)]-padding-[clearLeftButton(==imageButton)]",
            "H:|-column3-[updateRightButton(==imageButton)]-padding-[clearRightButton(==imageButton)]",
            "H:|-column4-[updateWidthButton(==imageButton)]-padding-[clearWidthButton(==imageButton)]",
            "H:|-margin-[list]-margin-|",
            "H:|-margin-[importButton(==button)]-spacing-[exportButton(==button)]",
            "H:[closeButton(==button)]-margin-|",
            "V:|"
                "-margin-"
                "[filterSearchBox]"
                "-spacing-"
                "[line]"
                "-spacing-"
                "[updateAllButton(==imageButton)]"
                "-padding-"
                "[list]"
                "-spacing-"
                "[importButton]"
                "-margin-"
            "|",
            "V:|"
                "-margin-"
                "[prioritizeProblemsCheckBox(==filterSearchBox)]",
            "V:"
                "[line]"
                "-spacing-"
                "[clearAllButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
                "[updateLeftButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
                "[clearLeftButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
                "[updateRightButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
                "[clearRightButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
                "[updateWidthButton(==imageButton)]",
            "V:"
                "[line]"
                "-spacing-"
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
        self.populateList()
        self.w.open()

    def closeButtonCallback(self, sender):
        self.w.close()

    def populateList(self, sender=None):
        searchPattern = self.w.filterSearchBox.get()
        glyphNames = [name for name in self.font.glyphOrder if name in self.layer]
        for glyphName in sorted(self.layer.keys()):
            if glyphName not in glyphNames:
                glyphNames.append(gyphName)
        if searchPattern:
            glyphNames = [
                glyphName
                for glyphName in glyphNames
                if fnmatch.fnmatchcase(glyphName, searchPattern)
            ]
        if self.w.prioritizeProblemsCheckBox.get():
            problems = []
            noProblems = []
            for glyphName in glyphNames:
                data = self.getDataForGlyphName(glyphName)
                if data["leftHasProblem"] or data["rightHasProblem"] or data["widthHasProblem"]:
                    problems.append(data)
                else:
                    noProblems.append(data)
            data = problems + noProblems
        else:
            data = [
                self.getDataForGlyphName(glyphName)
                for glyphName in glyphNames
            ]
        self._inInternalDataUpdate = True
        self.w.list.set(data)
        self._inInternalDataUpdate = False

    def updateAllData(self):
        self._inInternalDataUpdate = True
        for container in self.w.list:
            self.getDataForGlyphName(container["name"], container)
        self._inInternalDataUpdate = False

    def getDataForGlyphName(self, glyphName, container=None):
        if container is None:
            container = dict(
                name=glyphName,
                left=None,
                leftHasProblem=False,
                right=None,
                rightHasProblem=False,
                width=None,
                widthHasProblem=False
            )
        glyph = self.layer[glyphName]
        left, leftHasProblem = visualizeFormula(
            glyph,
            "leftMargin",
            formulas.getFormula(glyph, "leftMargin")
        )
        container["left"] = left
        container["leftHasProblem"] = leftHasProblem
        right, rightHasProblem = visualizeFormula(
            glyph,
            "rightMargin",
            formulas.getFormula(glyph, "rightMargin")
        )
        container["right"] = right
        container["rightHasProblem"] = rightHasProblem
        width, widthHasProblem = visualizeFormula(
            glyph,
            "width",
            formulas.getFormula(glyph, "width")
        )
        container["width"] = width
        container["widthHasProblem"] = widthHasProblem
        for k, v in container.items():
            if v is None:
                container[k] = ""
        return container

    # ----
    # Edit
    # ----

    _inInternalDataUpdate = False

    def listEditCallback(self, sender):
        if self._inInternalDataUpdate:
            return
        selection = sender.getSelection()[0]
        container = sender[selection]
        glyphName = container["name"]
        glyph = self.layer[glyphName]
        left = container.get("left", "")
        if left:
            left = str(left)
            formulas.setFormula(glyph, "leftMargin", left)
        else:
            formulas.clearFormula(glyph, "leftMargin")
        right = container.get("right", "")
        if right:
            right = str(right)
            formulas.setFormula(glyph, "rightMargin", right)
        else:
            formulas.clearFormula(glyph, "rightMargin")
        width = container.get("width", "")
        if width:
            width = str(width)
            formulas.setFormula(glyph, "width", width)
        else:
            formulas.clearFormula(glyph, "width")
        self.updateAllData()

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
        for glyph in self.layer:
            formulas.clearFormula(glyph, "leftMargin")
            formulas.clearFormula(glyph, "rightMargin")
            formulas.clearFormula(glyph, "width")
        path = path[0]
        f = open(path, "r")
        text = f.read()
        f.close()
        formulas.layerFromString(self.layer, text)
        self.updateAllData()

    def exportButtonCallback(self, sender):
        directory = os.path.dirname(self.font.path)
        fileName = os.path.splitext(os.path.basename(self.font.path))[0] + ".spacestation"
        vanilla.dialogs.putFile(
            resultCallback=self._exportCallback,
            parentWindow=self.w,
            directory=directory,
            fileName=fileName
        )

    def _exportCallback(self, path):
        if not path:
            return
        glyphOrder = list(self.font.glyphOrder)
        for name in sorted(self.layer.keys()):
            if name not in glyphOrder:
                glyphOrder.append(name)
        text = formulas.layerToString(self.layer, glyphOrder)
        f = open(path, "w")
        f.write(text)
        f.close()


red = AppKit.NSColor.redColor()

def visualizeFormula(glyph, attr, formula):
    if not formula:
        return formula, False
    calculatedValue = formulas.calculateFormula(
        glyph,
        formula,
        formulas.getAngledAttrIfNecessary(glyph.font, attr)
    )
    needColor = False
    if calculatedValue is None:
        needColor = True
    else:
        value = formulas.getMetricValue(glyph, attr)
        if tools.roundint(value) != tools.roundint(calculatedValue):
            needColor = True
    if needColor:
        formula = AppKit.NSAttributedString.alloc().initWithString_attributes_(
            formula,
            {AppKit.NSForegroundColorAttributeName : red}
        )
    return formula, needColor
