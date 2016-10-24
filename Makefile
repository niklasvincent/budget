test-all:
	./tests/run-tests.sh

virtualenv:
	virtualenv venv
	. ./venv/bin/activate && pip install -r requirements.txt
