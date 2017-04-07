----------------------------------------------------------------
-- Status for host:
--     0 Unassigned
--     1 Down
--     2 Maintenance
--     3 Up
--     4 NonResponsive
--     5 Error
--     6 Installing
--     7 Failed
--     8 Reboot
--     9 Preparing for maintenance
--     10 Non Operational
--     11 PendingApproval
--     12 Initializing
--     13 Connecting
--     14 InstallingOS
--     15 Kdumping

WITH hosts_unavailable AS (
    SELECT
        vds_name, status
    FROM
        vds
    WHERE status=2 or
          status=5 or
          status=7 or
          status=9 or
          status=10
)
SELECT
    vds_name, host_status_temp.text
FROM
    hosts_unavailable
LEFT JOIN
    host_status_temp ON hosts_unavailable.status = host_status_temp.id;
