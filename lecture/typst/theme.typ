// Typst slide chrome — dark classroom theme (low-vision friendly).
// WCAG AA contrast; avoid pure #000/#FFF halation;
// Atkinson Hyperlegible for letter distinction; larger type + open leading.

#let bg = rgb("#121212")          // near-black (not pure #000 — less halation)
#let ink = rgb("#F2F2F2")         // off-white body (not pure #FFF)
#let muted = rgb("#B8B8B8")       // secondary text; still strong on #121212 (~9:1)
#let accent = rgb("#8EC8E8")      // soft cyan — high luminance on dark; not deep navy
#let soft = rgb("#1E1E1E")        // elevated panel (MC answer box)
#let soft-stroke = rgb("#8EC8E8")

#let page-margin = (x: 0.7cm, y: 0.45cm)

// Sans for slides: Atkinson Hyperlegible (designed for low vision).
// Fallback chain if font missing on another machine.
#let font-sans = ("Atkinson Hyperlegible", "Liberation Sans", "TeX Gyre Heros", "Roboto")
#let font-math = ("New Computer Modern Math", "DejaVu Math TeX Gyre")

#let slides(
  course: "RESCEU GW lensing school",
  week: none,
  title: none,
  author: "Otto A. Hannuksela",
  body,
) = {
  set page(
    paper: "presentation-16-9",
    fill: bg,
    margin: page-margin,
    header: none,
    footer: context {
      set align(right)
      set text(size: 11pt, fill: muted, font: font-sans)
      let n = counter(page).get().first()
      let total = counter(page).final().first()
      [#n / #total]
    },
  )

  // Large slide type + open leading for projection / low vision.
  set text(font: font-sans, size: 20pt, fill: ink, weight: "regular")
  set par(justify: false, leading: 0.7em)
  set list(tight: true, marker: ([•], [–], [·]), spacing: 0.65em)
  set enum(tight: true)
  set math.equation(numbering: none)
  show math.equation: set text(fill: ink, font: font-math)
  // Inline: slash fractions; display/block: stacked vertical (Typst default).
  show math.equation.where(block: false): set math.frac(style: "horizontal")

  show heading.where(level: 1): it => {
    set text(font: font-sans, weight: "bold", size: 26pt, fill: ink)
    block(below: 0.3em, width: 100%, it.body)
    block(
      width: 100%,
      height: 2pt,
      fill: accent,
      spacing: 0pt,
    )
  }

  body
}

#let slide-title(body) = {
  heading(level: 1, body)
}
