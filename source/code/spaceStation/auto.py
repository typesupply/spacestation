from spaceStation.formulas import getFormula, getReferencesInFormula, splitReference
from spaceStation import SpaceStationError

# -----------
# Application
# -----------

def calculateLayer(layer):
    sequence = getResolutionSequence(layer)
    for group in sequence:
        for reference in group:
            glyphName, attr = splitReference(reference)


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


layer = CurrentLayer()
r = getResolutionSequence(layer)
for i in r:
    print(len(i), i)