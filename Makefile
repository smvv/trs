
BUILD=build/

# Fix pdflatex search path
TEXINPUTS := "$(TEXINPUTS):docs"
TEXFLAGS  := -halt-on-error -interaction=nonstopmode -file-line-error
TEXGREP   := grep -i ".*:[0-9]*:.*\|warning"

TGT_DIR :=
TGT_DOC :=

d := docs/
include base.mk
include $(d)/rules.mk

.PHONY: docs

all: docs

clean:
	rm -rf $(CLEAN)

docs: $(TGT_DOC)

$(TGT_DIR):
	mkdir -p $(TGT_DIR)

$(b)%.pdf: $(d)%.tex $(TGT_DIR)
	pdflatex $(TEXFLAGS) -output-directory `dirname $@` $< | ${TEXGREP} || true
