.PHONY: test coverage

test:
	pytest tests

coverage:
	pytest --cov=llmbrick --cov-report=term-missing --cov-report=html --cov-fail-under=80 tests

typecheck:
	mypy .

format:
	pre-commit run --files $(find llmbrick -type f)

.PHONY: website-deploy website-build

website-build:
	cd website && yarn build

website-deploy:
	cd website && USE_SSH=true yarn deploy
