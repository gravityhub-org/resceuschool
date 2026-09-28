#import "typst/slides.typ": *

#show: slides.with(
  course: "",
  week: "Gravitational-wave lensing · Lecture 1",
  title: "Theoretical minimum",
)

#title-slide([Gravitational-wave lensing], subtitle: [theoretical minimum])

// Make figure slideof the binary black hole with TT gauge and detector
#figure-slide(
  [How to get from merging black hole to a detector?],
  image("figures/bbh_polarisation_detector.pdf", width: 100%, height: 100%, fit: "contain"),
)

// Make a slide with Bayesian analysis (column figure left, text right) On the left, the famous GW150914 gravitational wave with illustration (from the internet/external source). On the right, text explaining the Bayesian analysis of gravitational wave data, including likelihood, prior, posterior, and evidence. 
#columns-slide(
  [How to get from a detector to merging black hole?],
  image("figures/external/gw150914_strain.pdf", width: 100%, height: 100%, fit: "contain"),
  credit: [Credit: Abbott et al. (LIGO/Virgo) — Phys. Rev. Lett. 116, 061102 (2016).],
)[
  - Bayesian theorem
    $
      p(phi | d) = (L(phi) pi(phi)) / Z
    $ <eq:bayes_theorem>
  - Likelihood $L(phi)$: probability of observing the data given a gravitational-wave strain.
  - Prior $pi(phi)$: Everything we know about binary black holes.
  - Posterior $p(phi|d)$: Everything we know about this binary black hole after considering the data.
  - Evidence $Z$: overall probability of the data under the model.
]

// Nested sampling + Laplace GIFs (figures only). Typst freezes GIF frames;
// `make lecture1.pdf` splices an Okular-playable LaTeX-animate page over this.
#figure-slide(
  [How to get from a detector to merging black hole?],
  image("figures/external/nested_sampling.gif", width: 100%, height: 100%, fit: "contain"),
  credit: [Credit: David Yallup],
)
// Nested sampling + Laplace GIFs (figures only). Typst freezes GIF frames;
// `make lecture1.pdf` splices an Okular-playable LaTeX-animate page over this.
#figure-slide(
  [How to get from a detector to merging black hole?],
  image("figures/laplace_approximation.gif", width: 100%, height: 100%, fit: "contain"),
  credit: [],
)

// Lens set up: Geometry 
#figure-slide(
  [What is geometrical time delay?],
  image("figures/lens_geometry.pdf", width: 100%, height: 100%, fit: "contain"),
)

// Lens set up: Fermat potential
#figure-slide(
  [What is lensing time delay?],
  image("figures/lens_geometry_deflection.pdf", width: 100%, height: 100%, fit: "contain"),
)

// Explain dimensionless variables and lens equation
#columns-slide(
  [Why are dimensionless quantities useful?],
  image("figures/lens_geometry_lens_equation.pdf", width: 100%, height: 100%, fit: "contain"),
)[
  - Dimensionless variables: 
   - $vec(x) = vec(theta) / theta_L$
   - $vec(y) = vec( beta ) / theta_L$
   - $psi_(L) (vec(x)) = psi(vec(x)) / theta_L^2$
  - What is the time delay?
  $
    Delta t(vec(x), vec(y)) = t_L [ 1/2  |vec(x) - vec(y)|^2 - psi_(L)(vec(x)) ].
  $ <eq:time_delay>
  - Where are the images?
  $
    vec(y) = vec(x) - nabla psi_(L) (vec(x)).
  $ <eq:lens_equation>
  - How magnified are the images?
  $
    |mu(vec(x))|^(-1) = |(partial vec(y)) / ( partial vec(x) ) |.
  $ <eq:magnification>
]

// MC Question: Suppose that the Singular isothermal sphere potential $psi(vec(theta)) = theta_E |vec(theta)|$. Where are the images in terms of the dimensionless variables $vec(x)$ and $vec(y)$?
#mc-question-slide(
  [Where are the images for a singular isothermal sphere?],
  image("figures/lens_geometry_lens_equation.pdf", width: 100%, height: 100%, fit: "contain"),
  (
    [$vec(y) = vec(x) - vec(x) / |vec(x)|$],
    [$vec(y) = vec(x) + theta_E vec(x) / |vec(x)|$],
    [$vec(y) = vec(x) - theta_E |vec(x)|$],
    [$vec(y) = vec(x) + theta_E |vec(x)|$],
  ),
)[
  - The lens equation is $vec(y) = vec(x) - nabla psi_(L) (vec(x))$.
  - For a singular isothermal sphere, $psi(vec(theta)) = theta_E |vec(theta)|$.
]

// Answer slide with derivation for images and for magnification and time delay
#mc-answer-slide(
  [Where are the images for a singular isothermal sphere?],
  image("figures/lens_geometry_lens_equation.pdf", width: 100%, height: 100%, fit: "contain"),
  [(a) $vec(y) = vec(x) - vec(x) / |vec(x)|$],
)[
  - For a singular isothermal sphere, $psi_(L)(vec(x)) = |vec(x)|$.
  - The gradient is $nabla psi_(L)(vec(x)) = vec(x) / |vec(x)|$.
  - Therefore, the lens equation becomes $vec(y) = vec(x) - vec(x) / |vec(x)|$.
  - Setting x-axis aligned with image, the solutions are:
  $
    x = y plus.minus 1.
  $
  - The magnification
  $
    |mu(vec(x))|^(-1) = |(partial vec(y)) / ( partial vec(x) ) | = |1-|x|^(-1)|.
  $
  - The time delay
  $
    Delta t(x, y) = t_L [ 1/2  |x - y|^2 - psi_(L)(x) ] 
  $
]

//   (`typst watch lecture1.typ` from lecture/)
// - #show: slides.with(…)  — footer = page n/N ONLY (no course chrome)
// - One constructor call = one PDF page (animation-slide = one page per frame)
// - No bullet reveals. Margins ≥ ~0.7 cm horizontal.
// - Content grid is height-bounded: figures MUST use
//     image(..., width: 100%, height: 100%, fit: "contain")
//   so tall art cannot overflow the page.
//
// TOPIC ARC (every *science* topic)
// 1. title-slide — transition
// 2. Observational/physics puzzle — real picture + motivating question (BEFORE jargon)
// Then in order (do not reorder):
//   puzzle/history → concept → technical illustration → math → example
//   → broader context → significance
// Mnemonic: puzzle → concept → picture → math → example → generalise → significance
//
// Logistics / syllabus opener: one Welcome + one combined content slide.
// Must not: title-slide per AI / help / schedule / “exciting now” micro-topic.
//
// 1. title-slide(title, subtitle: …)
// 2. figure-slide(title, figure, credit: …)     — title + still; credit if third-party
// 3. two-figure-slide(title, fig-a, fig-b, credit-a: …, credit-b: …)
//      — left fig | right fig (no bullets); shared credit: if both credit-a/b omitted
// 4. columns-slide(title, figure, credit: …)[ ] — ~55% fig | ~45% text (text VERTICALLY CENTERED)
// 5. two-figure-columns-slide(title, fig-a, fig-b, credit: …)[ ]
//      — two figs LEFT (side-by-side; stacked: true for vertical) | text RIGHT
// 6. mc-question-slide(title, figure, (…,), credit: …)[ context or [] ]
// 7. mc-answer-slide(title, figure, answer, credit: …)[ bullets ]
// 8. derivation-slide(title)[ guided steps ]
// 9. two-text-columns-slide(title, left, right) — two text columns (syllabus / compare)
// 10. movie-slide(title, poster, "….mp4", credit: …) — play MP4; filename at bottom
// 11. animation-slide(title, (frame1, …), credit: …)  — flipbook fallback (≤4 frames)
// 12. office-qa-slide() — LAST content slide: ask questions (before this footer)
//
// EXAMPLE FORMATTING (copy/adapt; every image: width+height 100%, fit: "contain")
//
// #title-slide([Topic name], subtitle: [optional short line])
//
// #figure-slide(
//   [Observational puzzle title?],
//   image("figures/….pdf", width: 100%, height: 100%, fit: "contain"),
//   credit: [Credit: Author/org — venue.],  // omit credit: for course-made figures
// )
//
// #two-figure-slide(
//   [Compare two stills],
//   image("figures/a.pdf", width: 100%, height: 100%, fit: "contain"),
//   image("figures/b.pdf", width: 100%, height: 100%, fit: "contain"),
//   credit-a: [Credit: …],
//   credit-b: [Credit: …],
// )
//
// #columns-slide(
//   [Concept: meaning then example],
//   image("figures/….pdf", width: 100%, height: 100%, fit: "contain"),
//   credit: [Credit: …],
// )[
//   - Term: short meaning in plain language.
//   - Example: one concrete case (numbers OK).
//   - Keep ≤ ~4 short bullets (text is vertically centered).
// ]
//
// #two-figure-columns-slide(
//   [Two figs left | text right],
//   image("figures/a.pdf", width: 100%, height: 100%, fit: "contain"),
//   image("figures/b.pdf", width: 100%, height: 100%, fit: "contain"),
//   credit: [Credit: …],          // or credit-a: / credit-b:; stacked: true
// )[
//   - Bullet about the pair.
//   - Second short bullet.
// ]
//
// #mc-question-slide(
//   [Question students can parse?],
//   image("figures/….pdf", width: 100%, height: 100%, fit: "contain"),
//   ([Choice A.], [Choice B.], [Choice C.], [Choice D.]),
//   credit: [Credit: …],
// )[]                                 // or [ - optional context before choices. ]
//
// #mc-answer-slide(
//   [Same question title?],
//   image("figures/….pdf", width: 100%, height: 100%, fit: "contain"),
//   [(b) Choice B.],
//   credit: [Credit: …],
// )[
//   - Why (b): one-line reason.
//   - Example / common trap if useful.
// ]
//
// #derivation-slide([Guided derivation title])[
//   - Name each symbol before it appears in an equation.
//   - $F = L \/ (4 pi r^2)$
//   - Next algebra step in words, then math.
// ]
//
// #two-text-columns-slide(
//   [Compare / syllabus],
//   [
//     *Left heading*
//     - Item one.
//     - Item two.
//   ],
//   [
//     *Right heading*
//     - Item one.
//     - Item two.
//   ],
// )
//
// #movie-slide(
//   [Motion title],
//   image("figures/media/foo_poster.jpg", width: 100%, height: 100%, fit: "contain"),
//   "figures/media/foo.mp4",
//   credit: [Credit: …],
// )
//
// #animation-slide(
//   [Flipbook title (≤4 frames)],
//   (
//     image("figures/media/foo_f0.png", width: 100%, height: 100%, fit: "contain"),
//     image("figures/media/foo_f1.png", width: 100%, height: 100%, fit: "contain"),
//   ),
//   credit: [Credit: …],
// )
//
// #office-qa-slide()   // once, last content slide, immediately before this RULES block
//
// STUDENT-FACING TEXT (strict)
// - Define every new term: meaning, then a concrete example.
// - Talk to the reader about physics — never narrate the slide/section/deck
//   (“why this section matters”, “in this slide we…”, “this chapter will cover…”,
//   “why the course looks this way”).
// - Self-contained: gloss people, named stars/objects, and missions on first use
//   (who/what + why here).
// - No course footer blurb; no yt-dlp / DVC / side-car / poster / file paths on the
//   student slide (same ban for notes + figure captions).
// - No unexplained metaphors. Question titles students can parse.
// - Full-bleed: no pedagogical caption under the figure.
// - Web/third-party media: REQUIRED short muted credit via credit: […]
//   (author/org + venue). Full URL/license still in figures/external/ATTRIBUTION.txt.
//   Course-made plots/TikZ: no credit line needed.
// - Long text → short bullets; derivations name each symbol before use.
// - Text on split slides is VERTICALLY CENTERED (keep ≤ ~4 short bullets so clip does not chop).
//
// MOTION / OKULAR
// - Typst embeds GIF/MP4 as a *static* first frame in PDF — will NOT play in Okular.
// - Flipbook: PNG frames + animation-slide; click/hold page advance to see motion.
// - fetch_media: set frames_start (skip logos) + frames_duration (stop before end cards).
//   Sampling only the first few seconds of an ESA/YouTube clip → duplicate logo stills.
// - Smooth classroom playback: play figures/media/*.mp4 on a second screen (DVC archive).
//
// FIGURES & MEDIA
// - Prefer lecture/figures/; symlink figures -> figures if compiling from a subdir
// - LARGE FILES → DVC (≥100 KiB / any video / frame dirs)
// - New web/YouTube: media manifest → fetch → dvc repro;
//   ATTRIBUTION.txt + on-slide credit: […]
//
// BUILD
// - cd lecture && typst watch lecture1.typ
// - make -C lecture
//
// WHEN ADDING A SLIDE
// - Matching constructor; ≤ ~4 bullets; define+example for new terms; no meta text.
// - Logistics: one Welcome + one combined slide (no title-slide per AI/help/schedule).
// - animation-slide ≤ 4 frames (constructor caps); avoid movie-page floods.
// - Text vertically centered in columns; ~55/45; no right-edge glyph clip.
// - Third-party image/movie → credit: on the constructor.
// - End every deck with #office-qa-slide() immediately before this RULES block.
// - Leave this RULES block at the end of the file.
// =============================================================================
