TGT_DIR += $(b)pybison $(b)jquery

PYBISON_INC := -Iexternal/pybison/src/c -I/usr/include/python2.7

build: $(b)pybison/bison_.so

BISON_OBJ := $(b)pybison/bison_.o $(b)pybison/bison_callback.o \
	$(b)pybison/bisondynlib-linux.o

$(b)pybison/bison_.so: $(BISON_OBJ)
	$(CC) $(CFLAGS) -shared -pthread -o $@ $^

$(BISON_OBJ): | $(b)pybison
	$(CC) $(CFLAGS) -o $@ -c $< -pthread -fPIC $(PYBISON_INC)

$(b)pybison/bisondynlib-linux.o: $(d)pybison/src/c/bisondynlib-linux.c
$(b)pybison/bison_callback.o: $(d)pybison/src/c/bison_callback.c
$(b)pybison/bison_.o: $(b)pybison/bison_.c

ifdef PYREX
py2c := pyrexc
else
ifdef CYTHON_0_14
py2c := cython --fast-fail --line-directives
else
py2c := cython -Wextra -Werror --fast-fail --line-directives
endif
endif

$(b)pybison/%.c: $(d)pybison/src/pyrex/%.pyx
	$(py2c) $(py2c_OPTS) -o $@ $<
	$(RM) $(@D)/*.so

build: $(b)jquery/jquery.min.js

$(b)jquery/jquery.min.js: $(d)jquery/version.txt | $(b)jquery
	$(MAKE) -C external/jquery
	ln -sf ../../../$(<D)/dist/jquery.min.js $@
