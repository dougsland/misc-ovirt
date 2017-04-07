CREATE TABLE host_status_temp (
    id NUMERIC, text varchar
);

INSERT INTO host_status_temp VALUES
    (0, 'Unassigned'),
    (1, 'Down'),
    (2, 'Maintenance'),
    (3, 'Up'),
    (4, 'NonResponsive'),
    (5, 'Error'),
    (6, 'Installing'),
    (7, 'InstallFailed'),
    (8, 'Reboot'),
    (9, 'PreparingForMaintenance'),
    (10, 'NonOperational'),
    (11, 'PendingApproval'),
    (12, 'Initializing'),
    (13, 'Connecting'),
    (14, 'InstallingOS'),
    (15, 'Kdumping');

CREATE TABLE host_type_temp (
    id NUMERIC, text varchar
);

INSERT INTO host_type_temp VALUES
    (0, 'rhel'),
    (1, 'ngn/rhvh'),
    (2, 'rhev-h');
