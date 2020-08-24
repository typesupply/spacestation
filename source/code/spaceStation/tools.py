def roundint(number):
    return int(round(number))

def writeFormulasToString(layer):
    from .formulas import getFormula
    font = layer.font
    order = list(font.glyphOrder)
    for name in sorted(font.keys()):
        if name not in order:
            order.append(name)
    text = []
    for glyphName in order:
        glyph = layer[glyphName]
        left = getFormula(glyph, "leftMargin")
        right = getFormula(glyph, "rightMargin")
        width = getFormula(glyph, "width")
        if not left and not right and not width:
            continue
        if text:
            text.append("")
        text.append("name: %s" % glyphName)
        if left:
            text.append("left: %s" % left)
        if right:
            text.append("right: %s" % right)
        if width:
            text.append("width: %s" % width)
    return "\n".join(text)

def readFormulasFromString(text, layer):
    from .formulas import setFormula
    glyph = None
    for line in text.splitlines():
        if ":" not in line:
            continue
        attr, formula = line.split(":", 1)
        formula = formula.strip()
        if attr == "name":
            name = formula
            if name not in layer:
                glyph = None
            else:
                glyph = layer[name]
        elif attr == "left":
            setFormula(glyph, "leftMargin", formula)
        elif attr == "right":
            setFormula(glyph, "rightMargin", formula)
        elif attr == "width":
            setFormula(glyph, "width", formula)