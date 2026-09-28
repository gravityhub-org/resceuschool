// Slide constructors — 1fr body (no overflow), Okular flipbook.

#import "theme.typ": *

// LaTeX-style \vec{x} (overrides Typst's column-vector vec).
#let vec(x) = math.arrow(x)

// ~55/45 — 65/35 clipped long bullets at the right page edge.
#let col-fig-frac = 55%
#let col-gutter = 0.4cm
#let col-text-size = 17.5pt

/// Light panel behind figures so dark-ink plots/schematics stay readable on dark slides.
#let figure-panel(figure) = {
  box(
    width: 100%,
    height: 100%,
    fill: rgb("#FAFAFA"),
    radius: 3pt,
    clip: true,
    inset: 0.15cm,
    align(center + horizon, figure),
  )
}

/// Student-facing source line for web / third-party media (not a full caption).
/// Keep short: author/org + venue. Full license stays in ATTRIBUTION.txt.
#let fig-credit(body) = {
  set text(size: 9.5pt, fill: muted, font: font-sans, weight: "regular")
  set par(leading: 0.45em)
  block(width: 100%, inset: (top: 0.28em, left: 0.05em, right: 0.05em), body)
}

#let _fig-with-credit(figure, credit) = {
  if credit == none {
    figure-panel(figure)
  } else {
    grid(
      rows: (1fr, auto),
      row-gutter: 0.12cm,
      figure-panel(figure),
      fig-credit(credit),
    )
  }
}

/// Title + 1fr body. Clip so figures cannot spill to the next page.
#let _content-page(title, body) = {
  page[
    #slide-title(title)
    #v(0.35em)
    #block(width: 100%, height: 1fr, clip: true, body)
  ]
}

/// Figure | text inside a height-bounded parent. Text **vertically centered** in
/// the right column (instructor preference; keep ≤ ~4 short bullets so
/// `_content-page` `clip: true` does not chop overflow).
///
/// Must use `(figure-fraction, 1fr)` — not `(X%, 100%-X%)` — because
/// `column-gutter` is *extra* width; two % tracks + gutter overflow the page
/// and `_content-page`'s `clip: true` chops trailing glyphs.
#let _split-left-text(left, body, figure-fraction: col-fig-frac) = {
  grid(
    columns: (figure-fraction, 1fr),
    column-gutter: col-gutter,
    rows: (1fr,),
    // Left: fill cell; right: vertically center the bullet block.
    align: (top, horizon),
    left,
    box(width: 100%, {
      set text(size: col-text-size)
      set par(leading: 0.65em)
      set list(tight: true, spacing: 0.55em)
      // Right inset: keep glyphs inside the text track (parent clips overflow).
      block(
        width: 100%,
        inset: (top: 0.12em, left: 0.1em, right: 0.45em),
        body,
      )
    }),
  )
}

#let _split-fig-text(figure, body, figure-fraction: col-fig-frac, credit: none) = {
  _split-left-text(
    _fig-with-credit(figure, credit),
    body,
    figure-fraction: figure-fraction,
  )
}

#let title-slide(title, subtitle: none) = {
  page(
    margin: (x: 0.8cm, y: 0.55cm),
    header: none,
  )[
    #align(center + horizon)[
      #block(width: 95%)[
        #set align(center)
        #set text(font: font-sans, weight: "bold", size: 52pt, fill: ink)
        #title
        #if subtitle != none {
          v(0.55em)
          set text(size: 22pt, weight: "regular", fill: muted)
          subtitle
        }
      ]
    ]
  ]
}

#let figure-slide(title, figure, credit: none) = {
  _content-page(title, _fig-with-credit(figure, credit))
}

/// Left figure | right figure (no text column). Credits under each panel.
/// Optional shared `credit:` under the whole row if per-side credits unused.
#let two-figure-slide(
  title,
  figure-a,
  figure-b,
  credit-a: none,
  credit-b: none,
  credit: none,
  left-fraction: 50%,
) = {
  let pair = grid(
    columns: (left-fraction, 1fr),
    column-gutter: col-gutter,
    rows: (1fr,),
    align: (top, top),
    _fig-with-credit(figure-a, credit-a),
    _fig-with-credit(figure-b, credit-b),
  )
  let body = if credit != none and credit-a == none and credit-b == none {
    grid(
      rows: (1fr, auto),
      row-gutter: 0.12cm,
      pair,
      fig-credit(credit),
    )
  } else {
    pair
  }
  _content-page(title, body)
}

#let columns-slide(title, figure, body, figure-fraction: col-fig-frac, credit: none) = {
  _content-page(
    title,
    _split-fig-text(figure, body, figure-fraction: figure-fraction, credit: credit),
  )
}

/// Two figures side-by-side (or stacked) in the left column; text on the right.
/// Same ~55/45 split + `1fr` text track as `columns-slide`.
///
/// Credits: shared `credit:` under the pair, or per-figure `credit-a:` / `credit-b:`.
#let two-figure-columns-slide(
  title,
  figure-a,
  figure-b,
  body,
  figure-fraction: col-fig-frac,
  credit: none,
  credit-a: none,
  credit-b: none,
  stacked: false,
) = {
  let pair = if stacked {
    grid(
      rows: (1fr, 1fr),
      row-gutter: 0.25cm,
      columns: (1fr,),
      figure-panel(figure-a),
      figure-panel(figure-b),
    )
  } else {
    grid(
      columns: (1fr, 1fr),
      column-gutter: 0.25cm,
      rows: (1fr,),
      figure-panel(figure-a),
      figure-panel(figure-b),
    )
  }

  let left = if credit != none {
    grid(
      rows: (1fr, auto),
      row-gutter: 0.12cm,
      pair,
      fig-credit(credit),
    )
  } else if credit-a != none or credit-b != none {
    if stacked {
      grid(
        rows: (1fr, 1fr),
        row-gutter: 0.25cm,
        columns: (1fr,),
        _fig-with-credit(figure-a, credit-a),
        _fig-with-credit(figure-b, credit-b),
      )
    } else {
      grid(
        columns: (1fr, 1fr),
        column-gutter: 0.25cm,
        rows: (1fr,),
        _fig-with-credit(figure-a, credit-a),
        _fig-with-credit(figure-b, credit-b),
      )
    }
  } else {
    pair
  }

  _content-page(
    title,
    _split-left-text(left, body, figure-fraction: figure-fraction),
  )
}

/// MC question: figure left | optional context bullets + (a)(b)(c)… right.
/// Trailing `[…]` = context (use `[]` when none). Keep ≤ ~4 short lines so clip does not chop.
#let mc-question-slide(
  title,
  figure,
  choices,
  body,
  figure-fraction: col-fig-frac,
  credit: none,
) = {
  let letters = "abcdefghijklmnopqrstuvwxyz"
  _content-page(title, {
    _split-fig-text(
      figure,
      {
        body
        // Spacer only when context present (empty `[]` → no extra gap above choices).
        if body != [] {
          v(0.55em)
        }
        for (i, choice) in choices.enumerate() {
          block(width: 100%, below: 0.45em)[*(#letters.at(i))* #choice]
        }
      },
      figure-fraction: figure-fraction,
      credit: credit,
    )
  })
}

#let mc-answer-slide(title, figure, answer, explanation, figure-fraction: col-fig-frac, credit: none) = {
  _content-page(title, {
    _split-fig-text(
      figure,
      {
        block(
          width: 100%,
          inset: (x: 0.45em, y: 0.35em),
          fill: soft,
          stroke: 1.5pt + soft-stroke,
          radius: 3pt,
          {
            set text(weight: "bold", fill: ink, size: col-text-size)
            answer
          },
        )
        v(0.45em)
        explanation
      },
      figure-fraction: figure-fraction,
      credit: credit,
    )
  })
}

#let derivation-slide(title, body) = {
  _content-page(title, {
    set text(size: 15.5pt)
    set par(leading: 0.5em)
    set list(tight: true, spacing: 0.45em)
    set math.equation(block: true)
    // Top-align: vertical centering + clip cuts off tall derivations.
    box(width: 100%, height: 100%, clip: true, {
      align(top, block(width: 100%, inset: (top: 0.1em), body))
    })
  })
}

/// Two text columns (no figure) — syllabus / compare lists. Top-aligned; denser type.
#let two-text-columns-slide(title, left, right, left-fraction: 50%) = {
  _content-page(title, {
    grid(
      columns: (left-fraction, 1fr),
      column-gutter: col-gutter,
      rows: (1fr,),
      align: (top, top),
      box(width: 100%, height: 100%, clip: true, {
        set text(size: 16.5pt)
        set par(leading: 0.58em)
        set list(tight: true, spacing: 0.42em)
        block(
          width: 100%,
          inset: (top: 0.08em, left: 0.05em, right: 0.35em),
          left,
        )
      }),
      box(width: 100%, height: 100%, clip: true, {
        set text(size: 16.5pt)
        set par(leading: 0.58em)
        set list(tight: true, spacing: 0.42em)
        block(
          width: 100%,
          inset: (top: 0.08em, left: 0.1em, right: 0.35em),
          right,
        )
      }),
    )
  })
}

/// Okular/PDF motion: one page per frame. Cap length so decks are not flooded
/// with near-duplicate movie stills (Typst freezes GIF anyway).
#let animation-max-frames = 4
#let animation-slide(title, frames, credit: none) = {
  let n = frames.len()
  let chosen = if n <= animation-max-frames {
    frames
  } else {
    // Evenly spaced subsample (first → last inclusive).
    range(animation-max-frames).map(i => {
      let idx = calc.round(i * (n - 1) / (animation-max-frames - 1))
      frames.at(int(idx))
    })
  }
  for frame in chosen {
    figure-slide(title, frame, credit: credit)
  }
}

/// Last content slide before the Copilot footer: ask questions (no figure).
/// Must appear once at the end of every classroom deck (before `slide_rules_footer`).
#let office-qa-slide() = {
  _content-page([Questions?], {
    set text(size: col-text-size)
    set par(leading: 0.65em)
    set list(tight: true, spacing: 0.55em)
    align(horizon, block(width: 100%, inset: (left: 0.1em, right: 0.45em), [
      - Please ask questions — after class, by email, or in office hours.
      - Instructor: Otto A. Hannuksela (`oahannuksela\@cuhk.edu.hk`).
    ]))
  })
}

/// One page: poster + MP4. Filename shown at bottom (clickable).
/// Attaches the MP4 into the PDF (`pdf.attach`) so Okular Attachments can open it;
/// poster / filename are links to the same path for external players (mpv/Okular).
/// Prefer this over `animation-slide` when a real `.mp4` exists.
///
/// `mp4` = path as used from the deck (e.g. `figures/media/foo.mp4`).
/// `slides.typ` lives in `presentation/typst/`, so attach/read use `../figures/…`.
#let movie-slide(title, poster, mp4, credit: none) = {
  let parts = mp4.split("/")
  let fname = parts.at(parts.len() - 1)
  let attach-src = if mp4.starts-with("figures/") { "../" + mp4 } else { mp4 }
  pdf.attach(
    fname,
    read(attach-src, encoding: none),
    relationship: "supplement",
    mime-type: "video/mp4",
    description: fname,
  )
  _content-page(
    title,
    grid(
      rows: (1fr, auto),
      row-gutter: 0.2cm,
      // Click poster → open MP4 (viewer / OS handler); path relative to the PDF.
      link(mp4, _fig-with-credit(poster, credit)),
      align(center, {
        set text(size: 12pt, fill: muted, font: font-sans, weight: "regular")
        link(mp4)[#raw(fname)]
      }),
    ),
  )
}
