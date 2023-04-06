.PHONY: clean


run_docker_services:
	@docker-compose -f dockerized_services/signal/docker-compose.yml --env-file .env up -d
	@docker-compose -f dockerized_services/kafka/docker-compose.yml --env-file .env up -d

stop_docker_services:
	@docker-compose -f dockerized_services/signal/docker-compose.yml --env-file .env down --remove-orphans
	@docker-compose -f dockerized_services/kafka/docker-compose.yml --env-file .env down --remove-orphans

clean:
	# stop docker services and remove persistent storage
	docker-compose -f dockerized_services/signal/docker-compose.yml --env-file .env down --volumes
	docker-compose -f dockerized_services/kafka/docker-compose.yml --env-file .env down --volumes
