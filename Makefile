BUILD=build/

# Fix pdflatex search path
TEXINPUTS := "$(TEXINPUTS):docs"
TEXFLAGS  := -halt-on-error -interaction=nonstopmode -file-line-error
TEXGREP   := grep -i ".*:[0-9]*:.*\|warning"

TGT_DIR :=
TGT_DOC :=

# Default target is 'all'. The 'build' target is defined here so that all
# sub rules.mk can add prerequisites to the 'build' target.
all:
build:

d := docs/
include base.mk
include $(d)/rules.mk

d := external/
include base.mk
include $(d)/rules.mk

d := tests/
include base.mk
include $(d)/rules.mk

.PHONY: doc

all: doc build

clean:
	rm -rf $(CLEAN)

$(TGT_DIR):
	mkdir -p $(TGT_DIR)
