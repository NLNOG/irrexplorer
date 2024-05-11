# Makefile for the IRR explorer development environment
.PHONY: clean
clean:
	docker system prune --all

.PHONY: start
start:
	docker-compose -f docker-compose.yml up -d

.PHONY: stop
stop:
	docker-compose -f docker-compose.yml down

.PHONY: rebuild
rebuild: stop clean start

.PHONY: dump_irrd_db
dump_irrd_db:
	docker exec postgres_irrd pg_dump -d irrd -U irrd -w > irrdb.sql

.PHONY: dump_irre_db
dump_irre_db:
	docker exec postgres_irre pg_dump -d irrexplorer -U irrexplorer -w > irrexplorer_db.sql