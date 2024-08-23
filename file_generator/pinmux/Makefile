# Makefile

# Target to run both commands
all: run_main_py3 run_pinmux_py2

# Run main.py with Python 3
run_main_py3:
	@python3 ./main.py

# Run pinmux_generator.py with Python 2
run_pinmux_py2:
	@python2 ./src/pinmux_generator.py -v -o ./file_generator/output

.PHONY: all run_main_py3 run_pinmux_py2
