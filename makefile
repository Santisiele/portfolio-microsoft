.PHONY: help install run test clean docker-build docker-run

help:
	@echo "make install       - install dependencies"
	@echo "make run           - run the app locally (http://localhost:5000)"
	@echo "make test          - run the test suite"
	@echo "make clean         - remove caches and session files"
	@echo "make docker-build  - build the Docker image"
	@echo "make docker-run    - run the app in Docker"

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	python -m pytest

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache flask_session

docker-build:
	docker build -t cartera .

docker-run:
	docker run -p 5000:5000 --env-file .env -e PORT=5000 cartera