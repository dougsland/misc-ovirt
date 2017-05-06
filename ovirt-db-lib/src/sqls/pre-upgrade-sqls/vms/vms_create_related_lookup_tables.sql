CREATE TABLE vms_status_temp (
    id NUMERIC, text varchar
);

INSERT INTO vms_status_temp VALUES
    (-1, 'Unassigned'),
    (0, 'Down'),
    (1, 'Up'),
    (2, 'PoweringUp'),
    (4, 'Paused'),
    (5, 'MigratingFrom'),
    (6, 'MigratingTo'),
    (7, 'Unknown'),
    (8, 'NotResponding'),
    (9, 'WaitForLaunch'),
    (10, 'RebootInProgress'),
    (11, 'SavingState'),
    (12, 'RestoringState'),
    (13, 'Suspended'),
    (14, 'ImageIllegal'),
    (15, 'ImageLocked'),
    (16, 'PoweringDown');
