# Space Station

A system for specifying glyph spacing values as formulas containing references to other glyphs. It is a work in progress.

## Formulas

A formula is a line of text defingin how a spacing value should be calculated. The formulas may contain the following parts:

- static numbers
- references to glyphs
- math symbols

The formula will be converted to a Python expression and evaluated to calculate the final value.

### Static Numbers

Numbers are numbers.

- `10`
- `10.01`
- `-10`
- `-10.01`

### References to Glyphs

Glyphs are referenced by name. The name will reference the glyph with the given name in the same layer as the target glyph.

- `S`
- `hyphen`
- `space`

A glyph name may have a symbol attached to it to indicate which metric value should be used. These are mapped to the following fontParts attributes:

Symbol   | fontParts Attribute
-------- | --------------------------------------------------------
`@left`  | `glyph.leftMargin` or `glyph.angledLeftMargin`
`@right` | `glyph.rightMargin` or `glyph.angledRightMargin`
`@width` | `glyph.width`

- `parenleft@right`
- `space.tab@width`

If no symbol is attached to a glyp name, the metric being set is implied.

Metric       | Implied Symbol
------------ | --------------
left margin  | `@left`
right margin | `@right`
width        | `@width`

If you want a glyph to reference itself, for example to make the right margin equal the left margin, enter the symbols without a glyph name.

- `@left`

### Math Symbols

The basic Python math symbols are allowed in formulas:

- `+`
- `-`
- `*`
- `/`
- `(`
- `)`

## Glyph Editor


## Apply To Font


## Import/Export


