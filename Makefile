include .env

start-db:
	@echo "--> Starting local GnS database..."
	docker-compose up -d db

stop-db:
	@echo "--> Starting local GnS database..."
	docker-compose stop db

init-db:
	@echo "--> Building local GnS database..."
	docker-compose up -d db && docker-compose -f docker-compose.yml run --rm --no-deps db \
		mysql --host=localhost \
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