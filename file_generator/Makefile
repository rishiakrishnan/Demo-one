# Makefile

# Target to run both commands
all: run_main_py3 run_pinmux_py2 run_ch_py3

# Run main.py with Python 3
run_main_py3:
	@python3 ./main.py

# Run pinmux_generator.py with Python 2
run_pinmux_py2:
	@python2 ./pinmux/src/pinmux_generator.py -v -o pinmux/test

run_ch_py3:
	@python3 ./ch.py

.PHONY: all run_main_py3 run_pinmux_py2
