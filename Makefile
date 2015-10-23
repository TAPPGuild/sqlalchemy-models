build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rf build dist bitjws_login.egg-info test/__pycache__ bitjws_login/__pycache__
	rm -rf test/*.pyc bitjws_login/*.pyc *.egg *~ bitjws_login/*~ test/*~

rst:
	pandoc --from=markdown_github --to=rst --output=README.rst README.md

schemas:
	python generate_schemas.py

