from .tools import roundint

# --------
# Lib Keys
# --------

expressionLibKeyStub = "com.typesupply.SpaceStation.expression."

def getExpression(glyph, attr):
    """
    Get the expression set in the glyph for the attr.
    """
    return glyph.lib.get(expressionLibKeyStub + attr)

def setExpression(glyph, attr, expression):
    """
    Set the expression in the glyph for the attr.
    """
    key = expressionLibKeyStub + attr
    if expression is None:
        if key in glyph.lib:
            del glyph.lib[key]
    else:
        glyph.lib[key] = expression

def clearExpressions(glyph, attr=None):
    """
    Clear the expression for the attr from the glyph.
    If no attr is given, all attrs will be cleared.
    """
    if attr is not None:
        attrs = [attr]
    else:
        attrs = symbolToAttribute.values()
    for attr in attrs:
        key = expressionLibKeyStub + attr
        if key in glyph.lib:
            del glyph.lib[key]

# -----------
# Expressions
# -----------

mathSymbols = """
+
-
*
/
(
)
""".strip().splitlines()

symbolToAttribute = {
    ".left" : "leftMargin",
    ".right" : "rightMargin",
    ".width" : "width"
}

attributeToSymbol = {}
for symbol, attr in symbolToAttribute.items():
    attributeToSymbol[attr] = symbol

def splitExpression(expression):
    """
    Split an expression into parts.
    """
    expression = expression.strip()
    expression = expression.split("#", 1)[0]
    if not expression:
        return []
    for symbol in mathSymbols:
        expression = expression.replace(symbol, " " + symbol + " ")
    expression = [i for i in expression.split(" ") if i]
    return expression

def getReferencesInExpression(expression):
    """
    Get glyphs referenced by an expression.
    """
    expression = splitExpression(expression)
    references = set()
    for i in expression:
        if i in mathSymbols:
            continue
        if i in symbolToAttribute:
            continue
        for symbol in symbolToAttribute.keys():
            if i.endswith(symbol):
                i = i[:-len(symbol)]
                break
        references.add(i)
    return references

def calculateMetricsExpression(glyph, expression, impliedAttr):
    """
    Calculate the value of an expression.
    """
    expression = splitExpression(expression)
    expression = _expandVariablesInExpression(glyph, glyph.layer, expression, impliedAttr)
    if expression is None:
        return None
    value = _evaluateExpression(expression)
    return value

def _expandVariablesInExpression(glyph, layer, expression, impliedAttr="leftMargin"):
    expanded = []
    for part in expression:
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

def _evaluateExpression(expression):
    text = " ".join(expression)
    value = eval(text)
    return value

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

def layerToString(layer, glyphOrder=None):
    """
    Write the expressions for all glyph in the layer to a string.
    """
    if glyphOrder is None:
        glyphOrder = layer.font.glyphOrder
    text = []
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
    Write the expressions defined for the glyph to a string.
    """
    text = [
        "> " + glyph.name
    ]
    for token in tokenOrder:
        attr = tokenToAttr[token]
        expression = getExpression(glyph, attr)
        line = token + " = "
        if not expression:
            line = "#" + line
        else:
            line += expression
            value = roundint(getMetricValue(glyph, attr))
            calculated = roundint(calculateMetricsExpression(glyph, expression, attr))
            if value != calculated:
                line = "#" + line
                line += " # value: {value} expected: {calculated}".format(value=value, calculated=calculated)
        text.append(line)
    return "\n".join(text)

def layerFromString(layer, text):
    """
    Load the expressions for all glyphs in the layer from the text.
    This does not apply the calculated expressions.
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
    Load the expressions for the glyph from the text.
    This does not apply the calculated expressions.
    """
    clearExpressions(glyph)
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            continue
        if "=" not in line:
            continue
        token, expression = line.split("=", 1)
        token = token.strip()
        expression = expression.strip()
        if token not in tokenToAttr:
            continue
        attr = tokenToAttr[token]
        setExpression(glyph, attr, expression)
