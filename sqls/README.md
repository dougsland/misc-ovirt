psql -U ${username} -d ${database} -h ${hostname} -W -f hosts_tables.sql
psql -U ${username} -d ${database} -h ${hostname} -W -f hosts_query_check_health.sql
psql -U ${username} -d ${database} -h ${hostname} -W -f cleanup.sql
