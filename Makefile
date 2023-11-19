.PHONY: pull build run

pull:
	git pull && git submodule update --init --recursive --remote

build:
	docker compose build
	docker compose -f docker-compose-test.yaml build

run:
	docker compose up

test:
	@docker compose -f docker-compose-test.yaml up -d
	@docker events --filter 'event=die' --filter "container=nycu-me-flask_app_test-1" > .event & echo $$! > .pidfile
	@while [ -z "$$(cat .event)" ]; do \
			sleep 1; \
	done
	@docker compose -f docker-compose-test.yaml logs flask_app_test
	@docker compose -f docker-compose-test.yaml down
	@kill -9 `cat .pidfile`
	@rm .pidfile
	@rm .event
