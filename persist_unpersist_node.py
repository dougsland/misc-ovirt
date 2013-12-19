from ovirt.node.utils import fs

file_name = "/etc/redhat-release"

fs.Config().unpersist(file_name)
fs.Config().persist(file_name)
