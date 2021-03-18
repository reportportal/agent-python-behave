SOURCES := behave_reportportal tests

.PHONY: check_fmt lint pydoc fmt tests tools

check: check_fmt lint pydoc tests

tools:
	pip install -r requirements-dev.txt

check_fmt:
	isort -c $(SOURCES)
	black --check $(SOURCES) -l 79

lint:
	flake8 $(SOURCES)
	pycodestyle $(SOURCES)

pydoc:
	pydocstyle behave_reportportal

fmt:
	isort $(SOURCES)
	black $(SOURCES) -l 79

tests:
	pytest --cov=behave_reportportal --cov-report=xml tests/units/
