SELECT
  row_number() OVER (ORDER BY vs.vds_name, n.name NULLs last) AS "NO.",
  n.name AS "Network",
  vs.vds_name AS "Host Name",
  sp.name AS "Data Center",
  nic.name AS "Attached to Nic",

  CASE
    WHEN
      nic.is_bond
    THEN
      (
        SELECT 'Bond(slaves:'||string_agg(slave.name, ', ')||')'
        FROM vds_interface slave
        WHERE slave.bond_name = nic.name AND slave.vds_id=nic.vds_id
      )
    WHEN
      n.vlan_id IS NOT NULL
    THEN
      'Vlan'
    ELSE
       'Regular Nic'
  END "Nic Type",

  ARRAY_TO_STRING(ARRAY[nic.mac_addr, (SELECT STRING_AGG(slave.mac_addr, ', ') FROM vds_interface slave WHERE slave.bond_name = nic.name AND slave.vds_id=nic.vds_id)], ', ') AS "Related MAC addresses",
  n.addr AS "Ipv4 Address",
  n.vlan_id AS "Vlan ID"
FROM
  network n
  LEFT OUTER JOIN storage_pool sp on n.storage_pool_id = sp.id
  LEFT OUTER JOIN vds_interface nic on n.name = nic.network_name
  LEFT OUTER JOIN vds_static vs on nic.vds_id = vs.vds_id
ORDER BY vs.vds_name, n.name
