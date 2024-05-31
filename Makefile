lint:
	-ruff check .
	-yamllint .github/workflows/*

pycheck:
	-pylint mcmlpy/__init__.py
	-pylint mcmlpy/mcml.py
	-pylint mcmlpy/mcmlv1.py
	-pylint mcmlpy/mcmlv2.py
	-pylint mcmlpy/mcsub.py

doccheck:
	-pydocstyle mcmlpy/mcmlpy.py
	-pydocstyle mcmlpy/__init__.py

html:
	cd docs && python -m sphinx -T -E -b html -d _build/doctrees -D language=en . _build
	open docs/_build/index.html

mco:
	mcml_v1 tests/mc-lost-test-v1-1.mci
	mv mc-lost-test-v1-1.mco tests
	mcml_v1 tests/mc-lost-test-v1-2.mci
	mv mc-lost-test-v1-2.mco tests
	mcml tests/mc-lost-test-v2-1.mci
	mv mc-lost-test-v2-1.mco tests
	mcml tests/mc-lost-test-v2-2.mci
	mv mc-lost-test-v2-2.mco tests

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf build
	rm -rf dist
	rm -rf docs/_build
	rm -rf docs/api
	rm -rf docs/.ipynb_checkpoints
	rm -rf docs/.jupyter
	rm -rf mcmlpy/__pycache__
	rm -rf tests/__pycache__

test:
	pytest tests/test_mcml.py
	pytest tests/test_mcmlv1.py
	pytest tests/test_mcmlv2.py
	pytest tests/test_mcsub.py

testall:
	make clean
	make test
	pytest --verbose tests/test_all_notebooks.py
	rm -rf __pycache__

rcheck:
	make clean
	make testall
	make lint
	make pycheck
	make doccheck
	touch docs/*ipynb
	touch docs/*rst
	make html
	check-manifest
	pyroma -d .
