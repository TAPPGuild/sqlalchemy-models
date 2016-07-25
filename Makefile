build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rf build dist sqlalchemy_models.egg-info test/__pycache__ sqlalchemy_models/__pycache__
	rm -rf test/*.pyc sqlalchemy_models/*.pyc *.egg *~ sqlalchemy_models/*~ test/*~
	rm -f sqlalchemy_models/*definitions.json

rst:
	pandoc --from=markdown_github --to=rst --output=README.rst README.md

schemas:
	rm -f sqlalchemy_models/*definitions.json
	python sqlalchemy_models/util.py sqlalchemy_models/_definitions.json
