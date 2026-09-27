#import "typst/slides.typ": *

#show: slides.with(
  course: "",
  week: "Gravitational-wave lensing · Lecture 2",
  title: "Theoretical minimum",
)

#title-slide([Gravitational-wave lensing], subtitle: [theoretical minimum])



// =============================================================================
// SLIDE RULES (Copilot / agent footer) — keep at END of every deck
// (lecture1.typ / lecture2.typ — always both).
// Canonical copy: typst/slide_rules_footer.typ
// When rules change: update that file, then replace this block in each deck.
// =============================================================================
//
// FRAMEWORK
// - Dark theme: near-black bg (#121212), off-white text (#F2F2F2), soft cyan accent.
//   Font: Atkinson Hyperlegible (low-vision letter distinction). Larger type + open leading.
//   Figures sit on a light panel so dark-ink plots stay readable.
// - Typst only. Import: #import "typst/slides.typ": *
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
