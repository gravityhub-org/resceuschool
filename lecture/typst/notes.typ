// Typst chrome for printed / PDF notes (light theme).
// Slides use theme.typ + slides.typ (dark). Do not mix.
// Body + headings: black text + Times New Roman (serif). Accent only for puzzle bar / links.
// Soft pastel boxes: `#example` (cool) and `#significance` (warm) — not saturated.

#let ink = rgb("#000000")
#let muted = rgb("#333333")
#let accent = rgb("#333333") // links / puzzle bar — not blue headings
#let soft = rgb("#f4f6f8")
// Soft callout fills (print-friendly; not saturated).
#let soft-example = rgb("#eef4f8") // cool blue-grey
#let soft-example-edge = rgb("#8aa4b8")
#let soft-significance = rgb("#f7f3ea") // warm parchment
#let soft-significance-edge = rgb("#b8a888")

// Serif body for notes/book only. Slides keep Atkinson in theme.typ.
// Fallback chain if font missing on another machine.
#let font-body = ("Times New Roman", "Liberation Serif", "TeX Gyre Termes", "Libertinus Serif", "Georgia")
#let font-math = ("New Computer Modern Math", "DejaVu Math TeX Gyre")

/// Boxed display equation. Call as `#boxed-eq[$ F = L / (4 pi r^2) $]`.
/// Do **not** use `$ #rect[...][…] $` — that drops out of math mode (literal `r^2`).
#let boxed-eq(body) = {
  set align(center)
  block(
    width: 100%,
    inset: (y: 0.35em),
    {
      set align(center)
      block(
        stroke: 0.6pt + luma(120),
        inset: (x: 0.85em, y: 0.55em),
        body,
      )
    },
  )
}

/// Numbered worked example. Always its own block (starts on a new line).
/// `#example[ … ]` → _Example 1._ …
/// `#example(title: [61 Cygni])[ … ]` → _Example 2 (61 Cygni)._ …
/// Counter is per PDF (week handout or compiled book).
#let example-counter = counter("example")
#let example(title: none, body) = {
  example-counter.step()
  block(
    width: 100%,
    breakable: true,
    above: 0.9em,
    below: 0.7em,
    inset: (x: 0.7em, y: 0.55em),
    fill: soft-example,
    stroke: (left: 2.5pt + soft-example-edge),
    {
      set par(first-line-indent: 0em)
      context {
        let n = example-counter.get().first()
        let head = if title == none {
          [_Example #n._]
        } else {
          [_Example #n (#title)._]
        }
        head
        [ ]
        body
      }
    },
  )
}

/// A4 notes / compiled book wrapper.
/// `section-new-page`: if true, each level-1 heading (`=`) starts on a new page
/// (compiled book). Week handouts leave this false.
#let notes(
  title: none,
  author: "Otto A. Hannuksela",
  course: "RESCEU GW lensing school",
  date: none,
  section-new-page: false,
  body,
) = {
  set page(
    paper: "a4",
    margin: (x: 2.2cm, y: 2.2cm),
    numbering: "1",
    header: context {
      set text(size: 8.5pt, fill: muted, font: font-body)
      course
      line(length: 100%, stroke: 0.4pt + luma(180))
    },
  )

  set text(font: font-body, size: 11pt, fill: ink)
  set par(justify: true, leading: 0.7em, first-line-indent: 0em)
  set heading(numbering: "1.1")
  set math.equation(numbering: "(1)")
  show math.equation: set text(font: font-math)
  // Inline: slash fractions; display/block: stacked vertical (Typst default).
  show math.equation.where(block: false): set math.frac(style: "horizontal")
  // Named-formula cites: @eq:… → "Eq. N" (writers wrap as (@eq:…) in prose).
  show ref: it => {
    if it.element != none and it.element.func() == math.equation {
      link(
        it.element.location(),
        {
          [Eq.]
          h(0.2em)
          numbering("1", ..counter(math.equation).at(it.element.location()))
        },
      )
    } else {
      it
    }
  }
  set list(tight: true)
  show link: set text(fill: accent)
  // Captions flush left (not centered under the figure).
  show figure.caption: set align(left)

  // All heading levels: black (no blue headers)
  show heading.where(level: 1): it => {
    if section-new-page {
      pagebreak(weak: true)
    }
    set text(font: font-body, weight: "bold", size: 18pt, fill: ink)
    block(breakable: false, above: 1.6em, below: 0.8em, width: 100%, it)
  }
  show heading.where(level: 2): it => {
    set text(font: font-body, weight: "bold", size: 13pt, fill: ink)
    block(above: 1.1em, below: 0.55em, it)
  }
  show heading.where(level: 3): it => {
    set text(font: font-body, weight: "bold", size: 11.5pt, fill: ink)
    block(above: 0.9em, below: 0.4em, it)
  }

  if title != none {
    align(center)[
      #text(font: font-body, weight: "bold", size: 22pt, fill: ink, title)
      #if author != none {
        v(0.4em)
        text(size: 11pt, fill: ink, author)
      }
      #if date != none {
        v(0.2em)
        text(size: 10pt, fill: muted, date)
      }
    ]
    v(1.2em)
  }

  body
}

/// Short “why care?” lead-in (grey bar — no bold labels).
#let puzzle(body) = {
  block(
    width: 100%,
    inset: (x: 0.7em, y: 0.55em),
    fill: soft,
    stroke: (left: 2.5pt + luma(100)),
    {
      set text(style: "italic", fill: ink)
      set par(first-line-indent: 0em)
      body
    },
  )
  v(0.6em)
}

/// Optional end-of-arc callout (plain prose; no bold label). Soft warm box.
#let significance(body) = {
  block(
    width: 100%,
    inset: (x: 0.7em, y: 0.55em),
    fill: soft-significance,
    stroke: (left: 2.5pt + soft-significance-edge),
    {
      set text(fill: ink)
      set par(first-line-indent: 0em)
      body
    },
  )
  v(0.5em)
}
