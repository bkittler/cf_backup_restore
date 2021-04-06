#cf_backup_restore - Cloudflare - tool for backup / restore data on Cloudflare account / zones

cf_backup_restore is python tool to export and/or import data from Cloudflare account/zones 


## Installation

Please first clone repository :

git clone https://github.com/bkittler/cf_backup_restore

Install Python and install requierements :

pip install -r requirements.txt


## Usage

Export synthax: cf_backup_restore.py -t <token_id> -e <export_zone_id>
Import synthax: cf_backup_restore.py -t <token_id> -i <import_zone_id>

<token_id> is token for authentication

<export_zone_id> is the id of the zone you want to export. You can put all to export all zones

<import_zone_id> is the id of the zone you want to import. It is not possible to import all zones (too dangerous)


To see Help: cf_backup_restore.py -h


## Output files

The tool will create a directory (directories if you are exporting all zones) with date and name of the zone. 
In this directory two files will be created for each of the exported data types


dns-json.txt   -> raw json export for DNS entry
dns_reimport.txt   -> export cleaned to allow diffs between zones

firewallaccessrules.txt   -> raw json export for firewall access rules
firewallaccessrules_reimport.txt   -> export cleaned to allow diffs between zones

pagerules.txt   -> raw json export for Page rules
pagerules_reimport.txt   -> export cleaned to allow diffs between zones

pools.txt   -> raw json export for pools

monitors.txt   -> raw json export for monitors

load_balancers.txt   -> raw json export for loadbalancer


## Diff

To make diff between zone export, you can make :

diff -u <(sort -u 2021-XX-XX-xxx.com-xxxx/*_reimport.txt) <(sort -u 2021-XX-XX-xxx.com-xxxx/*_reimport.txt)

or for diff between two backup :

diff -u <(sort -u 2021-XX-XX-xxx.com-xxxx/*.txt) <(sort -u 2021-XX-XX-xxx.com-xxxx/*.txt)


## Warning :

- Type of data : For moment, only DNS, page rules, firewall rule, pools, monitors and loadbalancer was exported / imported

- Token authorization : Remember to put the read authorization to your token id (for export) and read / write for the use of import


## Dependencies :

please install python dependancies before run tool :

pip install -r requierements.txt 
