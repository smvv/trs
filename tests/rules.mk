TESTS=$(wildcard tests/test_*.py)
COVERAGE_OUTPUT_DIR := coverage
OMIT := --omit /usr/share/pyshared/*,/usr/lib64/portage/*

ifeq ($(findstring python-coverage,$(wildcard /usr/bin/*)), python-coverage)
COVERAGE=/usr/bin/python-coverage
else
COVERAGE=/usr/bin/coverage
endif

.PHONY: test coverage $(TESTS)

test: $(TESTS) build

coverage: ${COVERAGE} build
	mkdir ${COVERAGE_OUTPUT_DIR} 2>/dev/null || true
	${COVERAGE} erase
	for t in ${TESTS}; do \
		echo $$t; \
		${COVERAGE} ${OMIT} -x test.py $$t; \
		${COVERAGE} ${OMIT} -c; \
	done
	${COVERAGE} html ${OMIT} --dir ${COVERAGE_OUTPUT_DIR}

${COVERAGE}:
	@echo "Install package 'python-coverage' to generate a coverage report."
	@echo "On Debian/Ubuntu use: sudo apt-get install python-coverage"; false

$(TESTS): build; @python -m testrunner $@
