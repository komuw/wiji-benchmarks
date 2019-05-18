test:
	@printf "run flake8\n"
	@flake8 benchmarks/
	@printf "run pylint\n"
	@pylint --enable=E --disable=W,R,C --unsafe-load-any-extension=y benchmarks/
	@printf "run bandit\n"
	@bandit -r --exclude .venv -lll .
	@printf "run tests\n"
	@python -m unittest discover -v -s .