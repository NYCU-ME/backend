.PHONY: pull build run

pull:
	git pull && git submodule update --init --recursive --remote

build:
	docker compose build

run:
	docker compose up
