TGT_DIR += $(b)pybison

PYBISON_INC := -Iexternal/pybison/src/c -I/usr/include/python2.7

build: $(b)pybison/bison_.so $(b)pybison/bison.py

$(b)pybison/bison_.so: $(b)pybison/bison_.o $(b)pybison/bisondynlib-linux.o
	$(CC) $(CFLAGS) -shared -pthread -o $@ $^

$(b)pybison/bison.py: $(d)pybison/src/python/bison.py | $(b)pybison
	ln -s `realpath $<` $@

$(b)pybison/bisondynlib-linux.o $(b)pybison/bison_.o: | $(b)pybison
	$(CC) $(CFLAGS) -o $@ -c $< -pthread -fPIC $(PYBISON_INC)

$(b)pybison/bisondynlib-linux.o: $(d)pybison/src/c/bisondynlib-linux.c
$(b)pybison/bison_.o: $(b)pybison/bison_.c

ifdef PYREX
py2c := pyrexc
else
py2c := cython -Wextra -Werror --fast-fail --line-directives
endif

$(b)pybison/%.c: $(d)pybison/src/pyrex/%.pyx
	$(py2c) -o $@ $<

