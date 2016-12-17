test-all:
	. ./venv/bin/activate && ./tests/run-tests.sh

virtualenv:
	virtualenv venv
	. ./venv/bin/activate && pip install -r requirements.txt

docker:
	docker build -f Dockerfile -t nlindblad/budget .

travis: test-all
	docker build -f Dockerfile -t nlindblad/budget .
