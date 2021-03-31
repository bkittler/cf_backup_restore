#cf_backup_restore

cf_backup_restore is python tool to export and/or import data from Clooudflare account/zones 

Export synthax: cf_backup_restore.py -t <token_id> -e <export_zone_id>
Import synthax: cf_backup_restore.py -t <token_id> -i <import_zone_id>

<token_id> is token for authentication
<export_zone_id> is the id of the zone you want to export. You can put all to export all zones
<import_zone_id> is the id of the zone you want to import. It is not possible to import all zones (too dangerous)

To see Help: cf_backup_restore.py -h

Dependencies :

please pip install -r requierements.txt before run tool
