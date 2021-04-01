#! /usr/bin/env python
# coding utf-8

import sys
from sys import exit
import os
import os.path
import string
import datetime
import getopt
import json

from progress.bar import Bar
import CloudFlare

sys.path.insert(0, os.path.abspath('..'))

"""Python script to export and import datas for one specific zone / account"""
__author__ = "Benjamin Kittler"
__copyright__ = "Copyright 2021, KITTLER"
__credits__ = ["Benjamin Kittler"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Benjamin Kittler"
__email__ = "kittler @T gmail.com"
__status__ = "integration"

"""
todo
make function for each type of import or export
dont forget .gitignore
dont forget requierement.txt
prefer os.path.dirname(__file__) for ./ = where
check if token id is active

use logging and not print
import logging as lg
lg.basicConfig(level=lg.DEBUG)
don't use print but lg.critical("toto {}".format(e))
or lg.debug("message {}".format(variable))

debbug : import pdb; pdb.set_trace()
"""


def check(value):
    """
    Function to verify ID string contain only ascii letters, letter and digits.

    Parameters
    ----------
    value : string
        Function receive string value to verify.

    Returns
    -------
    bool
        return True if value contain only ascii letters, letter and digits.
        return False if value different of only ascii letters and digits.
    """
    for letter in value:
        # check ID string validity
        if letter not in string.ascii_letters and letter not in string.digits and letter not in '-':
            return False
    return True


def printhelp():
    """
    Function to print standard help

    Returns
    -------
    None.

    """
    print('\nExport synthax: cf_backup_restore.py -t <token_id> -e <export_zone_id>\nImport synthax: cf_backup_restore.py -t <token_id> -i <import_zone_id>\n\n<token_id> is token for authentication\n<export_zone_id> is the id of the zone you want to export. You can put all to export all zones\n<import_zone_id> is the id of the zone you want to import. It is not possible to import all zones (too dangerous)\n\nTo see Help: cf_backup_restore.py -h\n')
    sys.exit()


def main(argv):
    """
    function main to get arguments on command line and launch export or import function with good parameter.

    Parameters
    ----------
    argv :
        -t for token
        <token_id> is token for authentication

        -e for export
        <export_zone_id> is the id of the zone you want to export. You can put all to export all zones

        -i for import
        <import_zone_id> is the id of the zone you want to import. It is not possible to import all zones (too dangerous)

        Export synthax: cf_backup_restore.py -t <token_id> -e <export_zone_id>
        Import synthax: cf_backup_restore.py -t <token_id> -i <import_zone_id>

    Returns
    -------
    None.

    """
    token_id = ''
    export_zone_id = ''
    import_zone_id = ''
    try:
        opts, args = getopt.getopt(argv, "t:e:i:", ["tokenid=", "exportid=", "importid="])
    except getopt.GetoptError:
        printhelp()
    for opt, arg in opts:
        if opt == "-h":
            printhelp()
        elif opt in "-t":
            token_id = arg
            if token_id:
                print('Token ID found...')
            if (len(token_id) != 40 or check(token_id) is not True):
                exit('Token ID not valid...')
        elif opt in "-e":
            export_zone_id = arg
            if export_zone_id:
                print('Export...')
            if export_zone_id != '' or export_zone_id != 'all':
                if export_zone_id != 'all':
                    print('Export zone ID file is', export_zone_id)
            if (len(export_zone_id) != 32 or check(export_zone_id) is not True):
                if export_zone_id == 'all':
                    print('Export all zones...')
                else:
                    print('Export zone ID not valid...')
            if export_zone_id == 'all':
                zone_source = ''
            else:
                zone_source = export_zone_id
            try:
                cf = CloudFlare.CloudFlare(token=token_id)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('api error: %d %s' % (e, e))
            try:
                validid = cf.user.tokens.verify()
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('api error: %d %s' % (e, e))
            if validid['status'] != 'active':
                exit('Token ID not valid...')
            exportdata(cf, zone_source)
        elif opt in "-i":
            import_zone_id = arg
            if import_zone_id:
                print('Import...')
            if import_zone_id != '':
                if import_zone_id != 'all':
                    print('Import zone ID file is', import_zone_id)
            if (len(import_zone_id) != 32 or check(import_zone_id) is not True):
                if import_zone_id == 'all':
                    print('Import all zones not possible...')
                else:
                    print('Import zone ID not valid...')
            try:
                cf = CloudFlare.CloudFlare(token=token_id)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('api error: %d %s' % (e, e))
            try:
                validid = cf.user.tokens.verify()
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('api error: %d %s' % (e, e))
            if validid['status'] != 'active':
                exit('Token ID not valid...')
            importdata(cf, import_zone_id)


def importdata(cf, zone_dest):
    """
    Function to import data to specific zone

    Parameters
    ----------
    cf : cloudflare API session

    zone_dest : destination zone id where data will be imported

    Returns
    -------
    None.

    """
    allzones = '0'
    zones = cf.zones.get(params={'per_page': 1000})
    print("Searching for zones...")
    print("\n")
    # lister les zone
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']

        if zone_dest == '' or allzones == 1:
            zone_dest = zone['id']
            # Export of all zones
            allzones = 1

        if zone['id'] == zone_dest:
            # export of specific zone
            zone_id = zone['id']
            print("\n**********\n")
            print('-> Zone detected : {} - {}'.format(zone_id, zone_name))
            agree = input("\nAre you sure you want to import into this zone ? (yes or no)\n")
            if agree == 'yes':
                print('Import...')
                for f in os.listdir("./"):
                    if zone_name in f:
                        print(f)
                a = input('Indicate the directory to import :')
                if a in os.listdir("./"):
                    print("import of", a)

                    # DNS
                    print('\nDNS :')
                    dns_reimport = a + '/dns-json.txt'
                    try:
                        file = open(dns_reimport, "r")
                    except:
                        exit('open dns-json.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # close the file after read all lines
                    file.close()

                    # iterate on each line
                    for line in lines:
                        s = line.strip()

                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("issue \"", "issue ")
                        json_acceptable_string = json_acceptable_string.replace("\"\"", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        datajson = json.loads(json_acceptable_string)

                        if datajson['proxied'] == "True":
                            datajson['proxied'] = bool("True")
                        else:
                            datajson['proxied'] = bool("")
                        entriesToRemove = ('id', 'zone_id', 'zone_name', 'created_on', 'modified_on', 'locked', 'meta', 'proxiable')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        if datajson['proxied'] == "False":
                            datajson['proxied'] = bool("")

                        try:
                            cf.zones.dns_records.post(zone_id, data=datajson)
                        except CloudFlare.exceptions.CloudFlareAPIError as e:
                            if len(e) > 0:
                                sys.stderr.write('api error - more than one error value returned!\n')
                                for x in e:
                                    sys.stderr.write('api error: %d %s\n' % (x, x))
                            if str(e) == "DNS validation failed: See messages for details.":
                                print('-> {:<100} -> !! not imported !! -> DNS validation failed or Already exists'.format(datajson['name'] + " " + datajson['type'] + " " + datajson['content']))
                            if str(e) == "An A, AAAA, or CNAME record with that host already exists.":
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['name'] + " " + datajson['type'] + " " + datajson['content']))
                            else:
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['name'] + " " + datajson['type'] + " " + datajson['content']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                    # PAGERULES
                    print('\nPAGERULES :')
                    pagerules_reimport = a + '/pagerules.txt'
                    try:
                        file = open(pagerules_reimport, "r")
                    except:
                        exit('open pagerules.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # close the file after read all lines
                    file.close()

                    # iterate on each line
                    for line in lines:
                        s = line.strip()
                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        datajson = json.loads(json_acceptable_string)
                        entriesToRemove = ('id', 'created_on', 'modified_on')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        try:
                            cf.zones.pagerules.post(zone_id, data=datajson)
                        except CloudFlare.exceptions.CloudFlareAPIError as e:
                            if len(e) > 0:
                                sys.stderr.write('api error - more than one error value returned!\n')
                                for x in e:
                                    sys.stderr.write('api error: %d %s\n' % (x, x))
                            if str(e) == "Page Rule validation failed: See messages for details.":
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['targets'][0]['constraint']['value'] + " " + datajson['actions'][0]['id']))
                            else:
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['targets'][0]['constraint']['value'] + " " + datajson['actions'][0]['id']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                    # FIREWALLRULES
                    print('\nFIREWALLRULES :')
                    firewallaccessrules_reimport = a + '/firewallaccessrules.txt'
                    try:
                        file = open(firewallaccessrules_reimport, "r")
                    except:
                        exit('open firewallaccessrules.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # close the file after read all lines
                    file.close()

                    # iterate on each line
                    for line in lines:
                        s = line.strip()
                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        datajson = json.loads(json_acceptable_string)
                        entriesToRemove = ('id', 'paused', 'modified_on', 'allowed_modes', 'scope', 'created_on')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        try:
                            cf.zones.firewall.access_rules.rules.post(zone_id, data=datajson)
                        except CloudFlare.exceptions.CloudFlareAPIError as e:
                            if len(e) > 0:
                                sys.stderr.write('api error - more than one error value returned!\n')
                                for x in e:
                                    sys.stderr.write('api error: %d %s\n' % (x, x))
                            # print("e = ", e)
                            if str(e) == "firewallaccessrules.api.duplicate_of_existing":
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['configuration']['value']))
                            else:
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['configuration']['value']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                    # MONITORS
                    try:
                        account_id = zones[0]['account']['id']
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/account_id %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/account_id - %s - api call failed' % (e))

                    print('\nMONITORS :')
                    monitors_reimport = a + '/monitors.txt'
                    try:
                        file = open(monitors_reimport, "r")
                    except:
                        exit('open monitors.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # close the file after read all lines
                    file.close()
                    try:
                        account_id = zones[0]['account']['id']
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/account_id %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/account_id - %s - api call failed' % (e))

                    try:
                        listmonitors = cf.accounts.load_balancers.monitors.get(account_id)
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/MONITORS %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/MONITORS - %s - api call failed' % (e))
                    # iterate on each line
                    for line in lines:
                        s = line.strip()
                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        json_acceptable_string = json_acceptable_string.replace("None", "\"None\"")
                        datajson = json.loads(json_acceptable_string)
                        entriesToRemove = ('created_on', 'modified_on', 'id', 'disabled_at')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        if datajson['follow_redirects'] == "False": datajson['follow_redirects'] = bool("")
                        else: datajson['follow_redirects'] = bool("True")
                        if datajson['allow_insecure'] == "False": datajson['allow_insecure'] = bool("")
                        else: datajson['allow_insecure'] = bool("True")
                        #import pdb; pdb.set_trace()
                        if datajson['header'] == "None":
                                datajson.pop('header', None)
                        exist = 0
                        descr = 0
                        if len(listmonitors) != 0:
                            while descr < len(listmonitors):
                                if listmonitors[descr]['description'] == datajson['description']:
                                    print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']))
                                    exist = 1
                                descr=descr+1

                        else:
                            try:
                                if exist != 1:
                                    cf.accounts.load_balancers.monitors.post(account_id, data=datajson)
                            except CloudFlare.exceptions.CloudFlareAPIError as e:
                                if len(e) > 0:
                                    sys.stderr.write('api error - more than one error value returned!\n')
                                    for x in e:
                                        sys.stderr.write('api error: %d %s\n' % (x, x))
                                if str(e) == "monitors.api.duplicate_of_existing": print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']))
                                else: print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                    # POOLS
                    print('\nPOOLS :')
                    pools_reimport = a + '/pools.txt'
                    try:
                        file = open(pools_reimport, "r")
                    except:
                        exit('open pools.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # create a list aof pool for futur id search when push
                    poollist = []
                    # close the file after read all lines
                    file.close()
                    try:
                        account_id = zones[0]['account']['id']
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/account_id %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/account_id - %s - api call failed' % (e))
                    try:
                        pools = cf.accounts.load_balancers.pools.get(account_id)
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/POOLS %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/POOLS - %s - api call failed' % (e))
                    # iterate on each line
                    for line in lines:
                        s = line.strip()
                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        json_acceptable_string = json_acceptable_string.replace("None", "\"None\"")
                        datajson = json.loads(json_acceptable_string)
                        poollist.append(datajson['id'])
                        poollist.append(datajson['name'])
                        if datajson['check_regions'] == "None": datajson['check_regions'] == "['WNAM']"
                        entriesToRemove = ('created_on', 'modified_on', 'id')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        if datajson['enabled'] == "False": datajson['enabled'] = bool("")
                        else: datajson['enabled'] = bool("True")

                        for idx, orig in enumerate(datajson['origins']):
                            if orig['enabled'] == "False":
                                datajson['origins'][idx]["enabled"] = bool("")
                            else: datajson['origins'][idx]["enabled"] = bool("True")

                        exist = 0
                        descr = 0
                        if len(listmonitors) != 0:
                            while descr < len(pools):
                                if pools[descr]['description'] == datajson['description']:
                                    print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']))
                                    exist = 1
                                descr = descr + 1

                        else:
                            try:
                                if exist != 1: cf.accounts.load_balancers.pools.post(account_id, data=datajson)
                            except CloudFlare.exceptions.CloudFlareAPIError as e:
                                if len(e) > 0:
                                    sys.stderr.write('api error - more than one error value returned!\n')
                                    for x in e:
                                        sys.stderr.write('api error: %d %s\n' % (x, x))
                                if str(e) == "A pool with that name already exists: value not unique": print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']))
                                else: print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['description']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                    # LOADBALANCERS
                    print('\nLOADBALANCERS :')
                    loadbalancers_reimport = a + '/load_balancers.txt'
                    try:
                        file = open(loadbalancers_reimport, "r")
                    except:
                        exit('open load_balancers.txt failed')
                    # read each line of file
                    # lines contain all line of file
                    lines = file.readlines()
                    # close the file after read
                    file.close()
                    try:
                        pools = cf.accounts.load_balancers.pools.get(account_id)
                    except CloudFlare.exceptions.CloudFlareAPIError as e:
                        exit('/POOLS %d %s - api call failed' % (e, e))
                    except Exception as e:
                        exit('/POOLS - %s - api call failed' % (e))

                    # iterate on each line
                    for line in lines:
                        s = line.strip()
                        json_acceptable_string = s.replace("'", "\"")
                        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
                        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
                        datajson = json.loads(json_acceptable_string)
                        entriesToRemove = ('created_on', 'modified_on', 'id')
                        for k in entriesToRemove:
                            datajson.pop(k, None)
                        if datajson['enabled'] == "False": datajson['enabled'] = bool("")
                        else: datajson['enabled'] = bool("True")
                        if datajson['proxied'] == "False": datajson['proxied'] = bool("")
                        else: datajson['proxied'] = bool("True")

                        # replace id by name
                        if datajson['fallback_pool'] != "": datajson['fallback_pool'] = poollist[poollist.index(datajson['fallback_pool']) + 1]
                        # replace name by new id
                        for currentpool in pools:
                            if datajson['fallback_pool'] == currentpool['name']:
                                datajson['fallback_pool'] = currentpool['id']

                        listdefaultpool = datajson['default_pools']

                        # replace id by name
                        for fpool in datajson['default_pools']:
                            if fpool != "":
                                datajson['default_pools'][listdefaultpool.index(fpool)] = poollist[poollist.index(fpool)+1]

                        # replace name by new id
                        for idx, fpool2 in enumerate(datajson['default_pools']):
                            for currentpool2 in pools:
                                if fpool2 == currentpool2['name']:
                                    datajson['default_pools'][idx] = currentpool2['id']

                        try:
                            cf.zones.load_balancers.post(zone_id, data=datajson)
                        except CloudFlare.exceptions.CloudFlareAPIError as e:
                            if len(e) > 0:
                                sys.stderr.write('api error - more than one error value returned!\n')
                                for x in e:
                                    sys.stderr.write('api error: %d %s\n' % (x, x))
                            if str(e) == "A load balancer with that name already exists: value not unique":
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['name']))
                            else:
                                print('-> {:<100} -> !! not imported !! -> Already exists'.format(datajson['name']) + '\t\t api error: %d %s' % (e, e))
                    print('Done...')

                else:
                    print("Abort...")
                    exit(0)
            else:
                print("Abort...")
                exit(0)


def exportdata(cf, zone_source):
    """
    Function to export data from specific zone
    if all zones define (=all), data from all zone from this account was exported

    Parameters
    ----------
    cf : cloudflare API session

    zone_source : source zone id where data will be exported

    Returns
    -------
    None.

    """
    allzones = '0'
    zones = cf.zones.get(params={'per_page': 1000})
    # extract the zone_id which is needed to process that zone

    print("Searching for zones...")
    print("\n")
    # list all zone
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']

        # change zone source for each zone if all zone must be exported
        if zone_source == '' or allzones == 1:
            zone_source = zone['id']
            # detect all zone must be exported
            allzones = 1

        # Get all pagerules
        try:
            pagerules = cf.zones.pagerules.get(zone_id, params={'per_page': 1000})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/PAGE RULES %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/PAGE RULES  - %s - api call failed' % (e))

        # Get all access rules
        try:
            access_rules = cf.zones.firewall.access_rules.rules.get(zone_id, params={'per_page': 1000})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/ACCESS RULES %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/ACCESS RULES - %s - api call failed' % (e))

        # Get all loadbalancers
        try:
            load_balancers = cf.zones.load_balancers.get(zone_id, params={'per_page': 1000})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/LOAD BALANCER %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/LOAD BALANCER - %s - api call failed' % (e))

        # Get account id to permit to get monitors and pools
        try:
            account_id = zones[0]['account']['id']
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/account_id %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/account_id - %s - api call failed' % (e))

        # Get all monitors
        try:
            monitors = cf.accounts.load_balancers.monitors.get(account_id)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/MONITORS %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/MONITORS - %s - api call failed' % (e))

        # Get all pools
        try:
            pools = cf.accounts.load_balancers.pools.get(account_id)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/POOLS %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/POOLS - %s - api call failed' % (e))

        # launch export part only for source zone indicate on argument
        if zone['id'] == zone_source:
            zone_id = zone['id']
            print("\n**********\n")
            print('-> Zone detected : {} - {}'.format(zone_id, zone_name))

            # get date and create repository
            today = datetime.date.today()
            todaystr = today.isoformat()
            Datetime = datetime.datetime.now()
            timestr = Datetime.strftime('%H%M')
            repertoire = todaystr + "-" + zone_name + "-" + timestr
            os.makedirs(repertoire, exist_ok=True)

            # DNS part
            print("Searching for DNS entries...\n")
            # query for the zone name and expect only one value back
            try:
                zones = cf.zones.get(params={'name': zone_name, 'per_page': 1000})
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones.get %d %s - api call failed' % (e, e))
            except Exception as e:
                exit('/zones.get - %s - api call failed' % (e))

            if len(zones) == 0:
                exit('No zones found')

            # extract the zone_id which is needed to process that zone
            zone = zones[0]
            zone_id = zone['id']

            # request the DNS records from that zone
            try:
                dns_records = cf.zones.dns_records.get(zone_id, params={'per_page': 1000})
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.get %d %s - api call failed' % (e, e))

            # print the results - first the zone name
            progress_bar = Bar('Processing', max=len(dns_records), suffix='%(percent)d%%')
            # then all the DNS records for that zone
            for dns_record in dns_records:
                r_name = dns_record['name']
                r_type = dns_record['type']
                r_value = dns_record['content']
                r_id = dns_record['id']
                progress_bar.next()
                # write the dns file
                file_name = "dns.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(r_id + '\t' + r_name + '\t' + r_type + '\t' + r_value + '\n')

                # write DNS json file to mermit diff between export or manual import
                file_name2 = "dns-json.txt"
                file_name_on_rep2 = os. path. join(repertoire, file_name2)
                with open(file_name_on_rep2, 'a') as file:
                    file.write(str(dns_record) + '\n')
            progress_bar.finish()

            # PAGE RULES part
            print("\n\n")
            print("Searching for Pagerules...\n")
            file_name = "pagerules.txt"
            file_name_on_rep = os. path. join(repertoire, file_name)
            fichier = open(file_name_on_rep, "w")
            fichier.close()
            progress_bar = Bar('Processing', max=len(pagerules), suffix='%(percent)d%%')
            for pagerule in pagerules:
                pagerule_json = pagerule
                progress_bar.next()

                pagerule_json_send = {}
                pagerule_json_send['targets'] = pagerule_json['targets']
                pagerule_json_send['actions'] = pagerule_json['actions']
                pagerule_json_send['priority'] = pagerule_json['priority']
                pagerule_json_send['status'] = pagerule_json['status']

                # write pagerules file
                file_name = "pagerules.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(pagerule_json) + '\n')
                file_name = "pagerules_reimport.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(pagerule_json_send) + '\n')
            progress_bar.finish()

            # ACCESS RULES part
            print("\n\n")
            print("Searching for Firewall access rules...\n")
            file_name = "firewallaccessrules.txt"
            file_name_on_rep = os. path. join(repertoire, file_name)
            fichier = open(file_name_on_rep, "w")
            fichier.close()
            progress_bar = Bar('Processing', max=len(access_rules), suffix='%(percent)d%%')
            for access_rule in access_rules:
                access_rule_json = access_rule
                progress_bar.next()

                access_rule_json_send = {}
                access_rule_json_send['mode'] = access_rule_json['mode']
                access_rule_json_send['configuration'] = access_rule_json['configuration']
                access_rule_json_send['notes'] = access_rule_json['notes']

                # write access rule file
                file_name = "firewallaccessrules.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(access_rule_json) + '\n')
                file_name = "firewallaccessrules_reimport.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(access_rule_json_send) + '\n')
            progress_bar.finish()

            # LOADBALANCERS part
            print("\n\n")
            print("Searching for Loadbalancer...\n")
            file_name = "load_balancers.txt"
            file_name_on_rep = os. path. join(repertoire, file_name)
            fichier = open(file_name_on_rep, "w")
            fichier.close()
            progress_bar = Bar('Processing', max=len(load_balancers), suffix='%(percent)d%%')
            for load_balancer in load_balancers:
                load_balancer_json = load_balancer
                progress_bar.next()

                load_balancer_json_send = {}
                load_balancer_json_send['description'] = load_balancer_json['description']
                try:
                    load_balancer_json_send['ttl'] = load_balancer_json['ttl']
                except:
                    load_balancer_json_send['ttl'] = ''
                load_balancer_json_send['proxied'] = load_balancer_json['proxied']
                load_balancer_json_send['name'] = load_balancer_json['name']
                load_balancer_json_send['session_affinity'] = load_balancer_json['session_affinity']
                load_balancer_json_send['session_affinity_attributes'] = load_balancer_json['session_affinity_attributes']
                load_balancer_json_send['steering_policy'] = load_balancer_json['steering_policy']
                load_balancer_json_send['fallback_pool'] = load_balancer_json['fallback_pool']
                load_balancer_json_send['default_pools'] = load_balancer_json['default_pools']
                load_balancer_json_send['pop_pools'] = load_balancer_json['pop_pools']
                load_balancer_json_send['region_pools'] = load_balancer_json['region_pools']

                # write loadbalancers file
                file_name = "load_balancers.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(load_balancer_json) + '\n')
                file_name = "load_balancers_reimport.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(load_balancer_json_send) + '\n')
            progress_bar.finish()

            # POOLS part
            print("\n\n")
            print("Searching for Pools...\n")
            file_name = "pools.txt"
            file_name_on_rep = os. path. join(repertoire, file_name)
            fichier = open(file_name_on_rep, "w")
            fichier.close()
            progress_bar = Bar('Processing', max=len(pools), suffix='%(percent)d%%')
            for pool in pools:
                pool_json = pool
                progress_bar.next()

                pool_json_send = {}
                pool_json_send['description'] = pool_json['description']
                pool_json_send['name'] = pool_json['name']
                pool_json_send['enabled'] = pool_json['enabled']
                pool_json_send['minimum_origins'] = pool_json['minimum_origins']
                try:
                    pool_json_send['monitor'] = pool_json['monitor']
                except:
                    pool_json_send['monitor'] = ''
                pool_json_send['check_regions'] = pool_json['check_regions']
                pool_json_send['origins'] = pool_json['origins']
                pool_json_send['notification_email'] = pool_json['notification_email']
                try:
                    pool_json_send['notification_filter'] = pool_json['notification_filter']
                except:
                    pool_json_send['notification_filter'] = ''
                try:
                    pool_json_send['pool'] = pool_json['pool']
                except:
                    pool_json_send['pool'] = ''

                # write pools file
                file_name = "pools.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(pool_json) + '\n')
                file_name = "pools_reimport.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(pool_json_send) + '\n')
            progress_bar.finish()

            # MONITORS part
            print("\n\n")
            print("Searching for Monitors...\n")
            file_name = "monitors.txt"
            file_name_on_rep = os. path. join(repertoire, file_name)
            fichier = open(file_name_on_rep, "w")
            fichier.close()
            progress_bar = Bar('Processing', max=len(monitors), suffix='%(percent)d%%')
            for monitor in monitors:
                monitor_json = monitor

                progress_bar.next()

                monitor_json_send = {}
                monitor_json_send['description'] = monitor_json['description']
                monitor_json_send['type'] = monitor_json['type']
                monitor_json_send['method'] = monitor_json['method']
                monitor_json_send['path'] = monitor_json['path']
                monitor_json_send['header'] = monitor_json['header']
                try:
                    monitor_json_send['port'] = monitor_json['port']
                except:
                    pass
                monitor_json_send['timeout'] = monitor_json['timeout']
                monitor_json_send['retries'] = monitor_json['retries']
                monitor_json_send['interval'] = monitor_json['interval']
                monitor_json_send['expected_body'] = monitor_json['expected_body']
                monitor_json_send['expected_codes'] = monitor_json['expected_codes']
                monitor_json_send['follow_redirects'] = monitor_json['follow_redirects']
                monitor_json_send['allow_insecure'] = monitor_json['allow_insecure']

                # write monitor file
                file_name = "monitors.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(monitor_json) + '\n')
                file_name = "monitors_reimport.txt"
                file_name_on_rep = os. path. join(repertoire, file_name)
                with open(file_name_on_rep, 'a') as file:
                    file.write(str(monitor_json_send) + '\n')
            progress_bar.finish()

            print("\n\n")
            print("End of zone export...\n")

            if allzones == 0:
                print("\n\n")
                print("End of export of all zones....")
                exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
