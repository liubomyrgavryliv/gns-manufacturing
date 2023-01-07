#!/usr/bin/env bash

include .env

init-migrate:
	@echo "--> Make initial migrations..."
	docker-compose up -d && docker-compose -f docker-compose.yml exec backend python manage.py makemigrations && \
	docker-compose -f docker-compose.yml exec backend python manage.py migrate

start-db:
	@echo "--> Starting local GnS database..."
	docker-compose up -d db

stop-db:
	@echo "--> Starting local GnS database..."
	docker-compose stop db

init-db:
	@echo "--> Building local GnS database..."
	docker-compose up -d db && docker-compose -f docker-compose.yml run --rm --no-deps db \
		mysql --default-character-set=utf8 \
				--host=localhost \
				--port=3306 \
				--user=${DB_USER} \
				--password=${DB_PASSWORD} \
				--database=${DB_NAME} \
				< ./sql/workflow/01_init_db.sql

clean-db:
	@echo "--> Cleaning up local GnS database..."
	docker-compose up -d db && docker-compose -f docker-compose.yml run --rm --no-deps db \
		mysql --host=localhost \
				--port=3306 \
				--user=${DB_USER} \
				--password=${DB_PASSWORD} \
				--database=${DB_NAME} \
				--disable-column-names \
				< ./sql/workflow/02_cleanup_db.sql

grant-all:
	@echo "--> Granting all privilegies to user..."
	docker-compose up -d db && docker-compose -f docker-compose.yml run --rm --no-deps db \
		mysql -user root \
			  -password${DB_PASSWORD} \
			< ./sql/workflow/03_grant_all_permissions.sql

dump-prod-db:
	$(eval include ./.envs/.prod/.db)
	$(eval export $(shell sed 's/=.*//' ./.envs/.prod/.db))

	docker-compose -f docker-compose.yml run \
		-e MYSQL_DATABASE=${MYSQL_DATABASE} \
		-e MYSQL_USER=${MYSQL_USER} \
		-e MYSQL_PORT=${MYSQL_PORT} \
		-e MYSQL_HOST=${MYSQL_HOST} \
		-e MYSQL_PASSWORD=${MYSQL_PASSWORD} --rm --no-deps db backup

restore-local-db:
	# USAGE: make restore-local-db backup=backup_....sql

	docker-compose -f docker-compose.yml run --rm --no-deps db restore "${backup}"
