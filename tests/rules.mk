TESTS=$(wildcard tests/test_*.py)
COVERAGE_OUTPUT_DIR := coverage
PROFILER_OUTPUT_DIR := profiles
OMIT := /usr/share/pyshared/*,external/*

ifeq ($(findstring python-coverage,$(wildcard /usr/bin/*)), python-coverage)
COVERAGE=/usr/bin/python-coverage
RM=rm -rf
else
COVERAGE=/usr/bin/coverage
endif

CLEAN := $(CLEAN) $(COVERAGE_OUTPUT_DIR) $(PROFILER_OUTPUT_DIR)
TGT_DIR := $(TGT_DIR) $(PROFILER_OUTPUT_DIR)

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

profile-test-%: $(PROFILER_OUTPUT_DIR) build
	 python -m cProfile -s cumulative \
	 	 -o $(PROFILER_OUTPUT_DIR)/tests_test_$*.py.profile test.py tests/test_$*.py

profile-test-view-%: $(PROFILER_OUTPUT_DIR) build
	python utils/view_profile.py "$(PROFILER_OUTPUT_DIR)/tests_test_$*.py.profile"

profile-view-%: $(PROFILER_OUTPUT_DIR) build
	python utils/view_profile.py "$(PROFILER_OUTPUT_DIR)/src_$*.py.profile"

profile-%: $(PROFILER_OUTPUT_DIR) build
	 python -m cProfile -s cumulative \
	 	 -o $(PROFILER_OUTPUT_DIR)/src_$*.py.profile src/$*.py
