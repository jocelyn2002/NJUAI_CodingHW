# **DO NOT MODIFY**

NAME    := fish
SRCS    := $(shell find . -maxdepth 1 -name "*.c")
DEPS    := $(shell find . -maxdepth 1 -name "*.h") $(SRCS)
CFLAGS  += -O1 -std=gnu11 -ggdb -Wall -Werror -Wno-unused-result -Wno-unused-value -Wno-unused-variable
LDFLAGS += -lpthread

.PHONY: all git test clean commit-and-make

all: $(NAME)-64 $(NAME)-32
.DEFAULT_GOAL := commit-and-make
commit-and-make: git all

$(NAME)-64: $(DEPS) # 64bit binary
	gcc -m64 $(CFLAGS) $(SRCS) -o $@ $(LDFLAGS)

$(NAME)-32: $(DEPS) # 32bit binary
	gcc -m32 $(CFLAGS) $(SRCS) -o $@ $(LDFLAGS)
 
$(NAME)-64.so: $(DEPS) # 64bit shared library
	gcc -fPIC -shared -m64 $(CFLAGS) $(SRCS) -o $@ $(LDFLAGS)

$(NAME)-32.so: $(DEPS) # 32bit shared library
	gcc -fPIC -shared -m32 $(CFLAGS) $(SRCS) -o $@ $(LDFLAGS)

clean:
	rm -f $(NAME)-64 $(NAME)-32 $(NAME)-64.so $(NAME)-32.so

# **DO NOT MODIFY**

export COURSE := OS2020
export MODULE := Midterm
URL := 'http://ics.nju.edu.cn/%7ejyywiki'

submit:
	@curl -sSL '$(URL)/submit.sh' | bash

git:
	@git add $(shell find . -name "*.c") $(shell find . -name "*.h") -A --ignore-errors
	@while (test -e .git/index.lock); do sleep 0.1; done
	@(hostnamectl && uptime) | git commit -F - -q --author='tracer-nju <tracer@nju.edu.cn>' --no-verify --allow-empty
	@sync

