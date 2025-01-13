CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -Werror -O2 -fPIC
CFLAGS  += -Ic/include
PYTHON  ?= python3

UNAME := $(shell uname)
ifeq ($(UNAME),Darwin)
LIBEXT := dylib
SHARED := -dynamiclib
else
LIBEXT := so
SHARED := -shared
endif

LIB   := build/libroutekit.$(LIBEXT)
SRCS  := $(wildcard c/src/*.c)
HDRS  := $(wildcard c/include/*.h)
TESTS := $(patsubst c/tests/%.c,build/%,$(wildcard c/tests/test_*.c))

.PHONY: build test test-c clean
build: $(LIB)

$(LIB): $(SRCS) $(HDRS)
	@mkdir -p build
	$(CC) $(CFLAGS) $(SHARED) -o $@ $(SRCS) -lm

build/test_%: c/tests/test_%.c $(SRCS) $(HDRS) c/tests/check.h
	@mkdir -p build
	$(CC) $(CFLAGS) -Ic/tests -o $@ $< $(SRCS) -lm

test-c: $(TESTS)
	@for t in $(TESTS); do echo "== $$t"; $$t || exit 1; done

test: build test-c
	$(PYTHON) -m pytest -q -p no:cacheprovider tests

clean:
	rm -rf build
