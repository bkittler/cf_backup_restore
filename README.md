#cf_backup_restore - Cloudflare - tool for backup / restore data on Clooudflare account / zones

cf_backup_restore is python tool to export and/or import data from Cloudflare account/zones 

Export synthax: cf_backup_restore.py -t <token_id> -e <export_zone_id>
Import synthax: cf_backup_restore.py -t <token_id> -i <import_zone_id>

<token_id> is token for authentication

<export_zone_id> is the id of the zone you want to export. You can put all to export all zones

<import_zone_id> is the id of the zone you want to import. It is not possible to import all zones (too dangerous)


To see Help: cf_backup_restore.py -h


Warning :

- Type of data : For moment, only DNS, page rules, firewall rule, pools, monitors and loadbalancer was exported / imported

- Token authorization : Remember to put the read authorization to your token id (for export) and read / write for the use of import




Dependencies :

please install python dependancies before run tool :

pip install -r requierements.txt 
