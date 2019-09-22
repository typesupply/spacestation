from spaceStation.expressions import getExpression, getReferencesInExpression

class SpaceStationError(Exception): pass

# -----------
# Application
# -----------

def calculateLayer(layer):
    pass

# ---------------------
# Resolution Sequencing
# ---------------------

"""
XXX:
- need to look at .left and .right in sequencing
maybe this is done in the resolution sequencing by having left, right and width divisions in each loop
"""

maximumRecursionDepth = 20

def getResolutionSequence(layer, attr):
    glyphNames = [glyphName for glyphName in layer.keys() if getExpression(layer[glyphName], attr)]
    sequence = [glyphNames]
    for i in range(maximumRecursionDepth):
        glyphNames = getGlyphsNeedingCalculation(layer, attr, glyphNames)
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

def getGlyphsNeedingCalculation(layer, attr, glyphNames):
    found = set()
    for glyphName in glyphNames:
        if glyphName not in layer:
            continue
        glyph = layer[glyphName]
        expression = getExpression(glyph, attr)
        if expression:
            references = getReferencesInExpression(expression)
            if references:
                found |= references
    return found

def getDependenciesForGlyph(glyph, attr):
    expression = getExpression(glyph, attr)
    references = getReferencesInExpression(expression)
    return references


layer = CurrentLayer()
for i in getResolutionSequence(layer, "leftMargin"):
    print(len(i), i)
