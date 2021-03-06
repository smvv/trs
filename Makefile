BUILD=build/

CFLAGS := -pipe -Wall -Wextra -fstrict-aliasing

ifdef DEBUG
CFLAGS := -ggdb -g -fno-omit-frame-pointer -O2 ${CFLAGS}
else
CFLAGS := -g -fomit-frame-pointer -O3 ${CFLAGS}
endif

-include config.mk

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

.PHONY: all doc build clean pyclean distclean

all: doc build

distclean: clean pyclean

clean:
	rm -rf $(CLEAN)

pyclean:
	find -name \*.pyc -delete

$(TGT_DIR):
	mkdir -p $(TGT_DIR)
