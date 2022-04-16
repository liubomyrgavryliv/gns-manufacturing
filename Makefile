include .env

init-db:
	@echo "--> Building local GnS database..."
	docker-compose up -d db && docker-compose -f docker-compose.yml run --rm --no-deps db \
		mysql --host=localhost \
				--port=3306 \
				--user=${DB_USER} \
				--password=${DB_PASSWORD} \
				--database=${DB_NAME} \
				< ./sql/workflow/01_init_db.sql || \
	docker-compose down

start-db:
	@echo "--> Starting local GnS database..."
	docker-compose up db