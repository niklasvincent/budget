lint:
	. ./venv/bin/activate && pip install pep8 && pep8 --show-source --exclude=venv .

test-all:
	. ./venv/bin/activate && ./tests/run-tests.sh

virtualenv:
	virtualenv venv
	. ./venv/bin/activate && pip install -r requirements.txt

docker:
	docker build -f Dockerfile -t nlindblad/budget .

travis: lint test-all
	docker build -f Dockerfile -t nlindblad/budget .
