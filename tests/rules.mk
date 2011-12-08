TESTS=$(wildcard tests/test_*.py)
COVERAGE_OUTPUT_DIR := coverage
OMIT := /usr/share/pyshared/*,/usr/lib/pymodules/python2.7/sympy/*

ifeq ($(findstring python-coverage,$(wildcard /usr/bin/*)), python-coverage)
COVERAGE=/usr/bin/python-coverage
RM=rm -rf
else
COVERAGE=/usr/bin/coverage
endif

.PHONY: test coverage $(TESTS)

test: $(TESTS) build

ifeq ($(findstring python-coverage,$(wildcard /usr/bin/*)), python-coverage)
coverage: ${COVERAGE} build
	${COVERAGE} erase
	${RM} ${COVERAGE_OUTPUT_DIR}/*
	mkdir ${COVERAGE_OUTPUT_DIR} 2>/dev/null || true
	for t in ${TESTS}; do \
		echo $$t; \
		${COVERAGE} -x test.py $$t; \
		${COVERAGE} combine; \
	done
	${COVERAGE} html --omit=${OMIT} -d ${COVERAGE_OUTPUT_DIR}
else
coverage: ${COVERAGE} build
	mkdir ${COVERAGE_OUTPUT_DIR} 2>/dev/null || true
	${COVERAGE} erase
	for t in ${TESTS}; do \
		echo $$t; \
		${COVERAGE} --omit ${OMIT} -x test.py $$t; \
		${COVERAGE} --omit ${OMIT} -c; \
	done
	${COVERAGE} html --omit ${OMIT} --dir ${COVERAGE_OUTPUT_DIR}
endif

${COVERAGE}:
	@echo "Install package 'python-coverage' to generate a coverage report."
	@echo "On Debian/Ubuntu use: sudo apt-get install python-coverage"; false

$(TESTS): build; @python -m testrunner $@
