build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rf build dist sqlalchemy_login_models.egg-info test/__pycache__ sqlalchemy_login_models/__pycache__
	rm -rf test/*.pyc sqlalchemy_login_models/*.pyc *.egg *~ sqlalchemy_login_models/*~ test/*~
	rm -rf sqlalchemy_login_models/schemas/*.json


rst:
	pandoc --from=markdown_github --to=rst --output=README.rst README.md

schemas:
	python sqlalchemy_login_models/generate_schemas.py

