.PHONY: docs

TGT_DOC += $(b)proposal.pdf

doc: $(TGT_DOC)

$(b)%.pdf: $(d)%.tex $(TGT_DIR)
	pdflatex $(TEXFLAGS) -output-directory `dirname $@` $< | ${TEXGREP} || true
