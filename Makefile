.PHONY: test coverage

test:
	pytest tests

coverage:
	pytest --cov=llmbrick --cov-report=term-missing --cov-report=html --cov-fail-under=80 tests