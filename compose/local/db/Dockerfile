FROM mysql/mysql-server:8.0.28

COPY ./db/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

COPY ./compose/local/db/init.sh /docker-entrypoint-initdb.d
RUN sed -i 's/\r$//g' /docker-entrypoint-initdb.d/init.sh
RUN chown -R mysql:mysql /docker-entrypoint-initdb.d/init.sh

COPY ./sql/workflow/00_omit_full_group_by.sql /docker-entrypoint-initdb.d/00_omit_full_group_by.sql
RUN sed -i 's/\r$//g' /docker-entrypoint-initdb.d/00_omit_full_group_by.sql
RUN chown -R mysql:mysql /docker-entrypoint-initdb.d/00_omit_full_group_by.sql
