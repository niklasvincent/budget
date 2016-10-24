test-all:
	. ./venv/bin/activate && ./tests/run-tests.sh

virtualenv:
	virtualenv venv
	. ./venv/bin/activate && pip install -r requirements.txt
