from spaceStation.formulas import getFormula, calculateFormula,\
    getReferencesInFormula, splitReference,\
    setMetricValue
from spaceStation import SpaceStationError

# -----------
# Application
# -----------

def applyFormulasInLayer(layer):
    sequence = getResolutionSequence(layer)
    for group in sequence:
        for reference in group:
            glyphName, attr = splitReference(reference)
            glyph = layer[glyphName]
            formula = getFormula(glyph, attr)
            if formula:
                value = calculateFormula(glyph, formula, attr)
                setMetricValue(glyph, attr, value)

# ---------------------
# Resolution Sequencing
# ---------------------

maximumReferenceDepth = 20

def getResolutionSequence(layer):
    glyphNames = set()
    for glyphName in layer.keys():
        glyph = layer[glyphName]
        for attr in "leftMargin rightMargin width".split(" "):
            formula = getFormula(glyph, attr)
            if formula:
                if attr == "leftMargin":
                    a = "@left"
                elif attr == "rightMargin":
                    a = "@right"
                else:
                    a = "@width"
                glyphNames.add(glyphName + a)
                glyphNames |= getReferencesInFormula(formula, attr)
    sequence = [glyphNames]
    for i in range(maximumReferenceDepth):
        glyphNames = getGlyphsNeedingCalculation(layer, glyphNames)
        if not glyphNames:
            break
        else:
            sequence.append(glyphNames)
    if glyphNames:
        error = "Maximum reference depth exceeded. Could there be a circular reference among these glyphs?: %s" % repr(glyphNames)
        raise SpaceStationError(error)
    compressed = []
    previous = None
    for glyphNames in reversed(sequence):
        if previous is not None:
            glyphNames = [glyphName for glyphName in glyphNames if glyphName not in previous]
        compressed.append(glyphNames)
        previous = glyphNames
    return compressed

def getGlyphsNeedingCalculation(layer, glyphNames):
    found = set()
    for reference in glyphNames:
        glyphName, attr = splitReference(reference)
        if glyphName not in layer:
            continue
        glyph = layer[glyphName]
        formula = getFormula(glyph, attr)
        if formula:
            references = getReferencesInFormula(formula, attr)
            if references:
                found |= references
    return found

def getDependenciesForGlyph(glyph, attr):
    formula = getFormula(glyph, attr)
    references = getReferencesInFormula(formula, attr)
    return references
