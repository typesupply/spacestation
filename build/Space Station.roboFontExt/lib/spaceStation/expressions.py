# --------
# Lib Keys
# --------

expressionLibKeyStub = "com.typesupply.SpaceStation.expression."

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

def calculateMetricsExpression(glyph, expression, impliedAttr):
    expression = expression.strip()
    if not expression:
        return None
    for symbol in mathSymbols:
        expression = expression.replace(symbol, " " + symbol + " ")
    expression = [i for i in expression.split(" ") if i]
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
                if part.endswith(".width"):
                    attr = "width"
                    part = part[:-len(".width")]
                elif part.endswith(".left"):
                    attr = "leftMargin"
                    part = part[:-len(".left")]
                elif part.endswith(".right"):
                    attr = "rightMargin"
                    part = part[:-len(".right")]
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
    attr = getAngledAttrIfNecessary(glyph.font, attr)
    return getattr(glyph, attr)

def setMetricValue(glyph, attr, value):
    attr = getAngledAttrIfNecessary(glyph.font, attr)
    setattr(glyph, attr, value)

def getAngledAttrIfNecessary(font, attr):
    useAngledMargins = font.info.italicAngle != 0
    if useAngledMargins:
        if attr == "leftMargin":
            attr = "angledLeftMargin"
        elif attr == "rightMargin":
            attr = "angledRightMargin"
    return attr
