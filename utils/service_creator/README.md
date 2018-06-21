# Service creator tool

This script is responsible for creating zeroboot host services.

This script can also create the racktivity client services if not already present on the robot.

If pool flag is provided with pool name, all the hosts in the datafile will be added to that pool.

These services need to be made in advance and be present on the 0-robot and accessible for the script
    - Any zboot service defined in the data with the following template uid: github.com/zero-os/0-boot-templates/zeroboot_client/0.0.1
    - Any ssh-service defined in the data with the following template uid: github.com/zero-os/0-boot-templates/ssh_client/0.0.1

## CSV source file

All the configurations of the services can be inserted into one CSV file.

How the different services are detected is by the title in the first column.
The row underneath the service title has the names of the configurations for that service.
The rows underneath contain the data for the service, matching the configuration titles column indexes.

The different service configurations are separated/terminated by an empty line or EOF.

The titles are case insensitive.

The current supported service and config titles are:
 - `racktivity_data`: Racktivity client service data
    - `host_address`: address of the racktivity device
    - `user`: Username for the racktivity device
    - `password`: Password for the racktivity device
    - `port`: (optional) Client access port on the racktivity device 
 - `host_data`: racktivity host service data
    - `zboot_service`: zerboot service name
    - `racktivity_service`: racktivity client service name for the host
    - `mac`: mac address of the host
    - `ip`: local ip address of the host
    - `network`: network the host is in
    - `hostname`: hostname of the host
    - `racktivity_port`: racktivity port the client is connected to
    - `racktivity_powermodule`: (optional, only for SE models) powermodule on the racktivity device
    - `lkrn_url`: Boot url

## Usage

The parameters to the script are:
    - robot {str} : The name of the robot to connect to. (zrobot robot connect main http://127.0.0.1:6600 -> main). If 'debug' the robot will be a MagicMock()
    - data {str} : CSV file to read the host data from, according to the format described above
    - pool {str}: flag to indicate that all the hosts in the file will be added to a single pool, the string provided sets the pool service name.
