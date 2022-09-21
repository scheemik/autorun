TEMPLATE=./template2/template.tex

INPUTS = $(wildcard *.md)
TARGETS = $(patsubst %.md,%.pdf,$(INPUTS))
TEXFILES = $(patsubst %.md,%.tex,$(INPUTS))
BBLFILES = $(patsubst %.md,%.bbl,$(INPUTS))
MARKDOWN = "markdown+footnotes"
all: $(TARGETS)

%.pdf: %.tex
	latexmk -quiet -f -bibtex -pdf $<

%.tex: %.md $(TEMPLATE)
	pandoc --from $(MARKDOWN) --template $(TEMPLATE) --to latex $< -o $@

clean: 
	latexmk -CA -bibtex
	rm -f $(TEXFILES) $(BBLFILES)

.SECONDARY: