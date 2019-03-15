analysis:
	@printf "run flake8\n"
	@flake8 benchmarks/
	@printf "run pylint\n"
	@pylint --enable=E --disable=W,R,C --unsafe-load-any-extension=y benchmarks/