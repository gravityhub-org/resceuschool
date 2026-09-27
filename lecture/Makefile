TYPST ?= $(shell command -v typst 2>/dev/null || echo $(HOME)/.local/bin/typst)
REPO_ROOT := $(abspath ../../..)
PYTHON3 ?= python3

# Local symlink typst/ -> ../../common/typst so `typst watch lecture1.typ` needs no --root.
# Always two classroom meetings → two decks.
DECKS := lecture1 lecture2
PDFS := $(addsuffix .pdf,$(DECKS))

all: $(PDFS)

%.pdf: %.typ typst/theme.typ typst/slides.typ
	$(TYPST) compile $< $@

watch-lecture1: typst/theme.typ typst/slides.typ
	$(TYPST) watch lecture1.typ lecture1.pdf

watch-lecture2: typst/theme.typ typst/slides.typ
	$(TYPST) watch lecture2.typ lecture2.pdf

clean:
	rm -f lecture1.pdf lecture2.pdf main.pdf

.PHONY: all clean watch-lecture1 watch-lecture2
