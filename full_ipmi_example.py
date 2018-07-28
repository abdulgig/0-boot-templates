"""
Pre-requests:
- zboot machine which is as an example:
    - ubuntu machine 16.04
    - Create a zerotier nw and connect to it
    - Install JS9
    - Install zrobot
    - Run zrobot ex, `zrobot server start -D <zrobot-data-repo> -C <js9-config-repo> -T git@github.com:zero-os/0-boot-templates.git --auto-push`
    - Create zrobot client ex. `zrobot robot connect zero-boot http://127.0.0.1:6600`
- Router:
    - Configure this router.
    - Connect it to the same zerotier nw.
- List of hosts:
    example :[{"network":"10.2.0.0/16",
              "hostname":"ipmi-storage03",
              "mac":"ac:1f:6b:4b:75:2a",
              "ip":"10.2.20.43"}]
- Edit this script with your variables' values.

What is this script do?
- It creates a zboot pool which has all zboot_host_ipmi and turn all of them on to load the lkrn_url.
"""

from js9 import j
# lkrnurl
lkrn_url = 'https://bootstrap.gig.tech/krn/v1.4.1/c7c8172af1f387a6/farmer_id=eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJ0aHJlZWZvbGQuZmFybWVycyIsImV4cCI6MTUyNzI0ODQ5NCwiaXNzIjoiaXRzeW91b25saW5lIiwicmVmcmVzaF90b2tlbiI6IkNJbW9wQ3YzNGlOMXRubm9XWXlQcnZJcUFHN1MiLCJzY29wZSI6WyJ1c2VyOm1lbWJlcm9mOmtyaXN0b2YtZmFybSJdLCJ1c2VybmFtZSI6ImRlc3BpZWdrIn0.dyFuU8TWkvwuY4R9JLbohkrw5J-8XilXswfwFQyauAGfT43k495__l6Pv8DNKGwDliL5miaeYAhaOxStavMfjDJoc5_arqCKpiDBhDigRtSLirU6WNHLSth7_3nog25V'

hosts = [{"network":"10.2.0.0/16",
         "hostname":"ipmi-storage03",
         "mac":"ac:1f:6b:4b:75:2a",
         "ip":"10.2.20.43"}]


# ssh client params
router_ip = '' # zt ip
router_ssh_username = ''
router_ssh_password = ''

# zboot client params
zt_nw_id = ''
zt_token = ''

# IPMI client params
ipmi_username = ''
ipmi_password = ''

#hosts
hosts = [{"network":"10.2.0.0/16",
         "hostname":"ipmi-storage03",
         "mac":"ac:1f:6b:4b:75:2a",
         "ip":"10.2.20.43",
         "ipmi_username":ipmi_username,
         "ipmi_password":ipmi_password,
         "zb_ipmi_client": [],
         "zb_ipmi_host": [] }]

robot = j.clients.zrobot.robots['zero-boot']

print(' [*] create zerotier client')
data = {
  'token': zt_token
}
robot.services.create("github.com/zero-os/0-boot-templates/zerotier_client/0.0.1", "zboot1-zt", data=data)
print(' [*] zerotier client : zboot1-zt')

print(' [*] SSH client to the router')
data = {
  'host': router_ip,
  'login': router_ssh_username,
  'password': router_ssh_password
}
ssh_service = robot.services.create("github.com/zero-os/0-boot-templates/ssh_client/0.0.1", "zboot1-ssh", data=data)
print(' [*] SSH client : zboot1-ssh')

print(' [*] zboot client')
data = {
  'networkId': zt_nw_id,
  'sshClient' : 'zboot1-ssh', # ssh client instance name
  'zerotierClient': 'zboot1-zt', # zerotier client instance name
}
zboot_service = robot.services.create("github.com/zero-os/0-boot-templates/zeroboot_client/0.0.1", "zboot1-zb", data=data)
print(' [*] zboot client : zboot1-zb')


for host in hosts:
    print(' [*] Create ipmi client')
    ipmi_client_service_name = host['name']+'_ipmi_client'
    data = {
        "bmc": host['ip'], # ipmi interface address of the host
        "user": host['ipmi_username'],
        "password": host['ipmi_password'],
    }
    host['zb_ipmi_client'].append(robot.services.create("github.com/zero-os/0-boot-templates/ipmi_client/0.0.1", ipmi_client_service_name, data=data))
    print(' [*] ipmi client : {}'.format(ipmi_client_service_name))

    print(' [*] Create ipmi host')
    ipmi_hosts_service_name = []
    ipmi_host_service_name = host['name']+'_ipmi_host'
    data = {
        'zerobootClient': 'zboot1-zb', # zeroboot client instance name
        'ipmiClient': ipmi_client_service_name, # ipmi client instance name
        'network': host['network'],
        'hostname': host['username'],
        'mac': host['mac'],
        'ip': host['ip'],
        'lkrnUrl': lkrn_url,
    }
    host['zb_ipmi_host'].append(robot.services.create("github.com/zero-os/0-boot-templates/zeroboot_ipmi_host/0.0.1",ipmi_host_service_name, data=data))
    ipmi_hosts_service_name.append(ipmi_host_service_name)
    print(' [*] ipmi host : {}'.format(ipmi_host_service_name))

print(' [*] zboot pool ')
data = {
    'zerobootHosts': ipmi_hosts_service_name # list of installed zeroboot host instances ready for reservation.
}
pool_service = robot.services.create("github.com/zero-os/0-boot-templates/zeroboot_pool/0.0.1", "zboot1-pool", data=data)
print(' [*] zboot pool : zboot1-pool')

print(' [*] Install hosts and turn all of them ON')
for host in host['zb_ipmi_host']:
    host.schedule_action("install").wait(die=True).result
    host.schedule_action("power_cycle").wait(die=True).result
    host.schedule_action("power_status").wait(die=True).result
