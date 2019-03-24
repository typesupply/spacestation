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
    expression = _expandVariablesInExpression(glyph.layer, expression, impliedAttr)
    if expression is None:
        return None
    value = _evaluateExpression(expression)
    return value

def _expandVariablesInExpression(layer, expression, impliedAttr="leftMargin"):
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
                if part not in layer:
                    return None
                glyph = layer[part]
                value = getattr(glyph, attr)
            expanded.append(str(value))
    return expanded

def _evaluateExpression(expression):
    text = " ".join(expression)
    value = eval(text)
    return value
