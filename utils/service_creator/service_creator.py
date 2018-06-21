import sys
import csv
from argparse import ArgumentParser

from js9 import j

def main(argv):
    parser = ArgumentParser()
    parser.add_argument("-d", "--data", dest="data_file", help="CSV file to read the host data from", required=True)
    parser.add_argument("-r", "--robot", dest="robot_name", help="0-robot instance to use", required=True)
    parser.add_argument("-p", "--pool", dest="pool_name", help="Puts all hosts in a pool with provided name", required=False)

    args = parser.parse_args()

    if args.robot_name == "debug":
        from unittest.mock import MagicMock
        robot = MagicMock()
    else:
        robot = j.clients.zrobot.robots[args.robot_name]

    create_rack_services(robot, args.data_file)
    hosts = create_host_services(robot, args.data_file)

    if args.pool_name:
        add_hosts_pool_service(robot, hosts, args.pool_name)

def create_rack_services(robot, data_file):
    """Creates the racktivity clients defined in the CSV file
    
    Arguments:
        robot {ZRboot} -- Robot instance
        data_file {str} -- location of the CSV file
    """
    with open(data_file, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',')
        rack_data_found = False
        title_indexes = {}
        row_i = -1
        for row in rdr:
            row_i += 1
            # find racktivity data starting row
            if not rack_data_found:
                if str(row[0]).lower() == ('racktivity_data'):
                    print("racktivity_data header found at row %s" % str(row_i + 1))
                    rack_data_found = True
                continue

            # the column titles should be in  the next row
            if not title_indexes:
                col_i = 0
                for col in row:
                    if col.lower() == 'host_address':
                        title_indexes['host_address'] = col_i
                    if col.lower() == 'user':
                        title_indexes['user'] = col_i
                    if col.lower() == 'password':
                        title_indexes['password'] = col_i
                    if col.lower() == 'hostname':
                        title_indexes['hostname'] = col_i
                    if col.lower() == 'port':
                        title_indexes['port'] = col_i
                    col_i += 1
                
                # check required columns
                for item in ('host_address', 'user', 'password', 'hostname'):
                    try:
                        title_indexes[item]
                    except KeyError:
                        raise RuntimeError("key '%s' was not provided for the racktivity_data at row %s" % (item, str(row_i + 1)))
                
                continue

            # keep adding racktivity hosts till empty row or EOF
            if row[0] in (None, "") and row[1] in (None, ""):
                print('Racktivity client data ended at row %s' % str(row_i + 1))
                break

            # create racktivity client
            data={}
            data["username"] = row[title_indexes['user']]
            data["password"] = row[title_indexes['password']]
            data["host"] = row[title_indexes['host_address']]
            if title_indexes.get("port") and row[title_indexes["port"]]:
                data["port"] = int(row[title_indexes["port"]])

            robot.services.find_or_create(
                "github.com/zero-os/0-boot-templates/racktivity_client/0.0.1",
                row[title_indexes["hostname"]],
                data=data,
            )
        else:
            if not rack_data_found:
                print("No racktivity client data was found")
            else:
                print("Racktivity client data ended at last row")

def create_host_services(robot, data_file):
    """Creates the host services and adds them to a pool if pool_name provided
    
    Arguments:
        robot {ZRboot} -- Robot instance
        data_file {str} -- Location of CSV file
        pool_name {str} -- Name of the pool to add the hosts to

    Returns:
        [str] -- List of host service names created
    """
    hosts = []

    with open(data_file, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',')
        host_data_found = False
        title_indexes = {}
        row_i = -1
        for row in rdr:
            row_i += 1
            # find host data starting row
            if not host_data_found:
                if str(row[0]).lower() == ('host_data'):
                    print("host_data header found at row %s" % str(row_i + 1))
                    host_data_found = True
                continue

            # the column titles should be in the next row
            if not title_indexes:
                col_i = 0
                for col in row:
                    if col.lower() == 'zboot_service':
                        title_indexes['zboot_service'] = col_i
                    if col.lower() == 'racktivity_service':
                        title_indexes['racktivity_service'] = col_i
                    if col.lower() == 'mac':
                        title_indexes['mac'] = col_i
                    if col.lower() == 'ip':
                        title_indexes['ip'] = col_i
                    if col.lower() == 'network':
                        title_indexes['network'] = col_i
                    if col.lower() == 'hostname':
                        title_indexes['hostname'] = col_i
                    if col.lower() == 'racktivity_port':
                        title_indexes['racktivity_port'] = col_i
                    if col.lower() == 'racktivity_powermodule':
                        title_indexes['racktivity_powermodule'] = col_i
                    if col.lower() == 'lkrn_url':
                        title_indexes['lkrn_url'] = col_i
                    col_i += 1
                
                # check required columns
                for item in ('zboot_service', 'racktivity_service', 'mac', 'ip', 'network', 'racktivity_port', 'lkrn_url'):
                    try:
                        title_indexes[item]
                    except KeyError:
                        raise RuntimeError("key '%s' was not provided for the user_data at row %s" % (item, str(row_i + 1)))

                continue
            
            # keep adding racktivity hosts till empty row or EOF
            if row[0] in (None, "") and row[1] in (None, ""):
                print('Host data ended at row %s' % str(row_i + 1))
                break
            
            data = {}
            data["zerobootClient"] = row[title_indexes['zboot_service']]
            data["racktivityClient"] = row[title_indexes['racktivity_service']]
            data["mac"] = row[title_indexes['mac']]
            data["ip"] = row[title_indexes['ip']]
            data["hostname"] = row[title_indexes['hostname']]
            data["network"] = row[title_indexes['network']]
            data["racktivityPort"] = int(row[title_indexes['racktivity_port']])
            data["lkrn_url"] = row[title_indexes['lkrn_url']]
            if title_indexes.get("racktivity_powermodule") and row[title_indexes["racktivity_powermodule"]]:
                data["racktivityPowerModule"] = row[title_indexes["racktivity_powermodule"]]

            host_service = robot.services.create(
                "github.com/zero-os/0-boot-templates/zeroboot_racktivity_host/0.0.1",
                data["hostname"],
                data=data,
            )
            host_service.schedule_action('install').wait(die=True)

            hosts.append(data["hostname"])

        else:
            if not host_data_found:
                print("No host data was found")
            else:
                print("host data ended at last row")

    return hosts

def add_hosts_pool_service(robot, hosts, pool_name):
    """Creates the pool service if it doesn't exist and adds all provided hosts in that pool
    
    Arguments:
        robot {ZRboot} -- Robot instance
        hosts [str] -- List of hostnames to add to the pool
        pool_name {str} -- Name to give the pool service
    """
    pool_service = robot.services.find_or_create(
        "github.com/zero-os/0-boot-templates/zeroboot_pool/0.0.1",
        pool_name,
        data={}
    )

    for host in hosts:
        # add host to pool
        pool_service.schedule_action('add', args={'zboot_host': host}).wait(die=True)

if __name__ == "__main__":
    main(sys.argv)
