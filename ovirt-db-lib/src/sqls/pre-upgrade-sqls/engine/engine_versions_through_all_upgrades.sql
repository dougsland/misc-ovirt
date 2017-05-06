-- This script takes all records from schema_version, and groups them 'according' to time, when their execution ended.
-- But grouping would create I record per group, which is not desirable. Therefore we 'round' their execution end time
-- to 30 minutes intervals, and group records using this time. From each such group we extract version column having
-- 'maximum value'. Value of this column is numbers separated by underscore so ordering should be ok. Version field
-- contains major and minor numbers as first two, followed by script number. Only major and minor version is reported.
SELECT
  regexp_replace(max(version), '^(\d{2})(\d{2}).*$', '\1.\2')
FROM
  schema_version
GROUP BY
  round(extract (EPOCH FROM ended_at)/60/30)
ORDER BY
  round(extract (EPOCH FROM ended_at)/60/30);
