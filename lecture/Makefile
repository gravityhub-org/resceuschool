TYPST ?= $(shell command -v typst 2>/dev/null || echo $(HOME)/.local/bin/typst)
UV ?= uv
REPO_ROOT := $(abspath ..)
PYTHON := $(UV) run --project $(REPO_ROOT) python

DECKS := lecture1 
PDFS := $(addsuffix .pdf,$(DECKS))

LAPLACE_SCRIPT := figures/scripts/laplace_approximation.py
ANIM_SCRIPT := figures/scripts/build_okular_animate_slide.py
LAPLACE_GIF := figures/laplace_approximation.gif
ANIM_PDF := figures/nested_laplace_okular.pdf

all: $(PDFS)

# Laplace GIF (and still PDF) — analytical 1D/2D steps
$(LAPLACE_GIF) figures/laplace_approximation.pdf: $(LAPLACE_SCRIPT)
	$(PYTHON) $(LAPLACE_SCRIPT)

# Okular-playable full-slide animation pages (nested + Laplace)
$(ANIM_PDF): $(ANIM_SCRIPT) $(LAPLACE_GIF) figures/external/nested_sampling.gif lecture1.typ
	$(PYTHON) $(ANIM_SCRIPT) animate

# lecture1: Typst placeholder, then splice Okular animate page over the GIF slide
lecture1.typst.pdf: lecture1.typ typst/theme.typ typst/slides.typ $(LAPLACE_GIF)
	$(TYPST) compile lecture1.typ $@

lecture1.pdf: lecture1.typst.pdf $(ANIM_PDF)
	$(PYTHON) $(ANIM_SCRIPT) splice

watch-lecture1: typst/theme.typ typst/slides.typ
	$(TYPST) watch lecture1.typ lecture1.typst.pdf

clean:
	rm -f lecture1.pdf lecture1.typst.pdf main.pdf
	rm -f figures/nested_laplace_okular.pdf

.PHONY: all clean watch-lecture1
