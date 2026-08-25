.PHONY: install backend-dev frontend-dev lint format typecheck test build clean docker-up docker-down

install:
	cd backend && make install
	cd frontend && make install

backend-dev:
	cd backend && make dev

frontend-dev:
	cd frontend && make dev

lint:
	cd backend && make lint
	cd frontend && make lint

format:
	cd backend && make format
	cd frontend && make format

typecheck:
	cd backend && make typecheck
	cd frontend && make typecheck

test:
	cd backend && make test
	cd frontend && make test

build:
	cd backend && make build
	cd frontend && make build

clean:
	cd backend && make clean
	cd frontend && make clean

docker-up:
	docker compose up --build

docker-down:
	docker compose down
