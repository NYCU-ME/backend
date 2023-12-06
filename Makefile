.PHONY: pull build run

pull:
	git pull
	git submodule update --init images/flask/app
	git submodule update --remote

deploy:
	@chmod 777 ./data/elasticsearch
	@chmod 777 ./data/logs
	@chmod 777 ./data/zones/
	@chmod 777 ./config/named/keys/

init:
	@mkdir -p ./data/elasticsearch
	@mkdir -p ./data/logs
	@chmod 777 ./data/elasticsearch
	@chmod 777 ./data/logs
	@chmod 777 ./data/zones/
	@chmod 777 ./config/named/keys/
	@rm -f ./config/named/keys/*.key
	@rm -f ./config/named/keys/*.state
	@rm -f ./config/named/keys/*.private
	@rm -rf ./config/named/ddnskey.conf
	@cp ./config/flask/config.py.sample ./config/flask/config.py
	@tsig-keygen -a hmac-sha512 ddnskey > ./config/named/ddnskey.conf

build:
	docker compose build
	docker compose -f docker-compose-test.yaml build

run:
	docker compose up

daemon:
	docker compose up -d

stop:
	docker compose down

run-test:
	@docker compose -f docker-compose-test.yaml up -d
	@docker events --filter 'event=die' > .event & echo $$! > .pidfile
	@while [ -z "$$(cat .event | grep 'flask_app_test')" ]; do \
			sleep 1; \
	done
	@docker compose -f docker-compose-test.yaml ps -a | grep flask_app_test | egrep -o "Exited \(.*\)" | egrep -o "\(.*\)" | tr -d '()' > .test_result 
	@docker compose -f docker-compose-test.yaml logs flask_app_test
	@docker compose -f docker-compose-test.yaml down
	@test_result=$$(cat .test_result)
	@kill -9 `cat .pidfile`
	@rm .pidfile
	@rm .event

test: run-test
	@$(eval test_result := $(shell cat .test_result))
	@rm .test_result
	@exit $(test_result)
	
rm-db:
	rm -rf data/db/*
	rm -f data/zones/*.jbk
	rm -f data/zones/*.jnl
	rm -f data/zones/*.signed
	rm -rf data/logs/*
	rm -rf data/elasticsearch/*
