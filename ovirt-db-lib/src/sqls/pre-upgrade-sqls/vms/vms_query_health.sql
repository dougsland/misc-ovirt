----------------------------------------------------------------
-- Requires:
-- vms_create_related_lookup_tables.sql
--
-- Status for vms:
--
--  -1 Unassigned,
--   0 Down,
--   1 Up
--   2 PoweringUp
--   4 Paused
--   5 MigratingFrom
--   6 MigratingTo
--   7 Unknown
--   8 NotResponding
--   9 WaitForLaunch
--   10 RebootInProgress
--   11 SavingState
--   12 RestoringState
--   13 Suspended
--   14 ImageIllegal
--   15 ImageLocked
--   16 PoweringDown
--
-- All values defined in ovirt-engine project:
-- backend/manager/modules/common/src/main/java/org/ovirt/engine/core/common/businessentities/VMStatus.java

WITH vms_unavailable AS (
    SELECT
        vm_name, status
    FROM
        vms
    WHERE
        status=4 or
        status=14 or
        status=15
)
SELECT
    vm_name, vms_status_temp.text
FROM
    vms_unavailable
LEFT JOIN
    vms_status_temp ON vms_unavailable.status = vms_status_temp.id;
