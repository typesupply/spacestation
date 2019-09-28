from .tools import roundint

# -------------
# Lib Shortcuts
# -------------

formulaLibKeyStub = "com.typesupply.SpaceStation.formula."

def getFormula(glyph, attr):
    """
    Get the formula set in the glyph for the attr.
    """
    return glyph.lib.get(formulaLibKeyStub + attr)

def setFormula(glyph, attr, formula):
    """
    Set the formula in the glyph for the attr.
    """
    key = formulaLibKeyStub + attr
    if glyph.lib.get(key) == formula:
        return
    if formula is None:
        if key in glyph.lib:
            del glyph.lib[key]
    else:
        glyph.lib[key] = formula

def clearFormula(glyph, attr=None):
    """
    Clear the formula for the attr from the glyph.
    If no attr is given, all attrs will be cleared.
    """
    if attr is not None:
        attrs = [attr]
    else:
        attrs = symbolToAttribute.values()
    for attr in attrs:
        key = formulaLibKeyStub + attr
        if key in glyph.lib:
            del glyph.lib[key]

# --------
# Formulas
# --------

mathSymbols = """
+
-
*
/
(
)
""".strip().splitlines()

symbolToAttribute = {
    "@left" : "leftMargin",
    "@right" : "rightMargin",
    "@width" : "width"
}

attributeToSymbol = {}
for symbol, attr in symbolToAttribute.items():
    attributeToSymbol[attr] = symbol

def splitFormula(formula):
    """
    Split a formula into parts.
    """
    formula = formula.strip()
    formula = formula.split("#", 1)[0]
    if not formula:
        return []
    for symbol in mathSymbols:
        formula = formula.replace(symbol, " " + symbol + " ")
    formula = [i for i in formula.split(" ") if i]
    return formula

def calculateFormula(glyph, formula, impliedAttr):
    """
    Calculate the value of a formula.
    """
    formula = splitFormula(formula)
    formula = _convertReferencesToNumbers(glyph, glyph.layer, formula, impliedAttr)
    if formula is None:
        return None
    value = _evaluateFormula(formula)
    return value

def _evaluateFormula(formula):
    text = " ".join(formula)
    value = eval(text)
    return value

# ----------
# References
# ----------

def _convertReferencesToNumbers(glyph, layer, formula, impliedAttr="leftMargin"):
    expanded = []
    for part in formula:
        if part in mathSymbols:
            expanded.append(part)
        else:
            value = 0
            try:
                v = float(part)
                value = v
            except ValueError:
                attr = impliedAttr
                for symbol, a in symbolToAttribute.items():
                    if part.endswith(symbol):
                        attr = a
                        part = part[:-len(symbol)]
                        break
                if not part:
                    part = glyph
                elif part not in layer:
                    return None
                else:
                    part = layer[part]
                value = getMetricValue(part, attr)
            expanded.append(str(value))
    return expanded

def getReferencesInFormula(formula, impliedAttr):
    """
    Get glyphs referenced by a formula.
    """
    formula = splitFormula(formula)
    references = set()
    for i in formula:
        if i in mathSymbols:
            continue
        if i in symbolToAttribute:
            continue
        try:
            float(i)
            continue
        except ValueError:
            pass
        foundSymbol = False
        for symbol in symbolToAttribute.keys():
            if i.endswith(symbol):
                foundSymbol = True
                break
        if not foundSymbol:
            i += attributeToSymbol[impliedAttr]
        references.add(i)
    return references

def splitReference(reference):
    """
    Split a reference into a glyph name and attribute.
    """
    for symbol, attr in symbolToAttribute.items():
        if reference.endswith(symbol):
            reference = reference[:-len(symbol)]
            return reference, attr
    return reference, None

# -----
# Tools
# -----

def getMetricValue(glyph, attr):
    """
    Get the metric value for an attribute.
    """
    attr = getAngledAttrIfNecessary(glyph.font, attr)
    return getattr(glyph, attr)

def setMetricValue(glyph, attr, value):
    """
    Set the metric value for an attribute.
    """
    attr = getAngledAttrIfNecessary(glyph.font, attr)
    value = roundint(value)
    setattr(glyph, attr, value)

def getAngledAttrIfNecessary(font, attr):
    """
    Coerce "leftMargin" or "rightMargin" to
    "angledLeftMargin" or "angledRightMargin"
    if the font is italic.
    """
    useAngledMargins = font.info.italicAngle != 0
    if useAngledMargins:
        if attr == "leftMargin":
            attr = "angledLeftMargin"
        elif attr == "rightMargin":
            attr = "angledRightMargin"
    return attr

# ---
# I/O
# ---

syntax = """
# SYNTAX
# ------
# # = comment. Anything after # will be ignored.
# > = glyph name
# L = left margin
# R = right margin
# W = width
# 
# Empty lines have no meaning.
""".strip()

def layerToString(layer, glyphOrder=None):
    """
    Write the formulas for all glyph in the layer to a string.
    """
    if glyphOrder is None:
        glyphOrder = layer.font.glyphOrder
    text = [syntax + "\n\n\n"]
    for glyphName in glyphOrder:
        if glyphName not in layer:
            continue
        glyph = layer[glyphName]
        text.append(glyphToString(glyph))
    return ("\n\n".join(text))

tokenToAttr = dict(L="leftMargin", R="rightMargin", W="width")
tokenOrder = list("LRW")

def glyphToString(glyph):
    """
    Write the formulas defined for the glyph to a string.
    """
    text = [
        "> " + glyph.name
    ]
    for token in tokenOrder:
        attr = tokenToAttr[token]
        formula = getFormula(glyph, attr)
        line = token + " = "
        if not formula:
            line = "#" + line
        else:
            line += formula
            value = roundint(getMetricValue(glyph, attr))
            calculated = roundint(calculateFormula(glyph, formula, attr))
            if value != calculated:
                line = "#" + line
                line += " # value: {value} expected: {calculated}".format(value=value, calculated=calculated)
        text.append(line)
    return "\n".join(text)

def layerFromString(layer, text):
    """
    Load the formulas for all glyphs in the layer from the text.
    This does not apply the calculated formulas.
    """
    glyphs = {}
    currentGlyph = None
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            currentGlyph = line[1:].strip()
            glyphs[currentGlyph] = []
        elif currentGlyph is not None:
            glyphs[currentGlyph].append(line)
    for glyphName, text in glyphs.items():
        if glyphName not in layer:
            continue
        text = "\n".join(text)
        glyphFromString(layer[glyphName], text)

def glyphFromString(glyph, text):
    """
    Load the formulas for the glyph from the text.
    This does not apply the calculated formulas.
    """
    clearFormula(glyph)
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            continue
        if "=" not in line:
            continue
        token, formula = line.split("=", 1)
        token = token.strip()
        formula = formula.strip()
        if token not in tokenToAttr:
            continue
        attr = tokenToAttr[token]
        setFormula(glyph, attr, formula)
