from js9 import j

from zerorobot.template.base import TemplateBase
from zerorobot.template.state import StateCheckError

class ZerobootRacktivityHost(TemplateBase):

    version = '0.0.1'
    template_name = "zeroboot_racktivity_host"

    def __init__(self, name=None, guid=None, data=None):
        super().__init__(name=name, guid=guid, data=data)
        self.__zeroboot = None
        self.__network = None
        self.__racktivity = None
        self.__host = None

    @property
    def _zeroboot(self):
        """ Returns zeroboot client
        
        Returns:
            ZerobootClient -- zeroboot JS client
        """
        if not self.__zeroboot:
            self.__zeroboot = j.clients.zboot.get(self.data['zerobootClient'], interactive=False)
        return self.__zeroboot
    
    @property
    def _racktivity(self):
        """ Returns Racktivity client
        
        Returns:
            RacktivityClient -- racktivity JS client
        """
        if not self.__racktivity:
            self.__racktivity =  j.clients.racktivity.get(self.data['racktivityClient'], interactive=False)
        return self.__racktivity

    @property
    def _powermodule_id(self):
        """ Returns the Racktivity power module id
        returns None if empty.
        
        Returns:
            str -- Racktivity powermodule ID
        """
        pm = self.data.get('racktivityPowerModule')
        if pm and pm != "" :
            return pm
        else:
            return None

    @property
    def _network(self):
        """ Returns the zeroboot network of the host
        
        Returns:
            ZerobootClient.Network -- Zeroboot network
        """
        if not self.__network:
            self.__network =  self._zeroboot.networks.get(self.data['network'])

        return self.__network

    @property
    def _host(self):
        """ Returns zeroboot host for this service
        
        Returns:
            ZerobootClient.Host -- Zeroboot Host
        """
        if not self.__host:
             self.__host = self._network.hosts.get(self.data['hostname'])

        return  self.__host

    def validate(self):
        for key in ['zerobootClient', 'racktivityClient', 'mac', 'ip', 'network', 'hostname', 'racktivityPort']:
            if not self.data.get(key):
                raise ValueError("data key '%s' not specified." % key)

        # check if clients exists
        if self.data['zerobootClient'] not in j.clients.zboot.list():
            raise LookupError("No zboot client instance found named '%s'" % self.data['zerobootClient'])

        if self.data['racktivityClient'] not in j.clients.racktivity.list():
            raise LookupError("No racktivity client instance found named '%s'" % self.data['racktivityClient'])

    def install(self):
        # add host to zeroboot
        if self.data['hostname'] in self._network.hosts.list():
            if self.data['mac'] != self._host.mac:
                raise RuntimeError("Host was found in the network but mac address did not match")
            if self.data['ip'] != self._host.address:
                raise RuntimeError("Host was found in the network but ip address did not match")
        else:
            self._network.hosts.add(self.data['mac'], self.data['ip'], self.data['hostname'])

        if self.data.get('lkrnUrl'):
            self._host.configure_ipxe_boot(self.data['lkrnUrl'])

        self.state.set('actions', 'install', 'ok')
        self.data['powerState'] = self.power_status()

    def uninstall(self):
        # remove host from zeroboot
        self._network.hosts.remove(self.data['hostname'])
        self.state.delete('actions', 'install')

    def host(self):
        """ Returns the hostname of the node
        
        Returns:
            str -- hostname
        """
        self.state.check('actions', 'install', 'ok')

        return self.data['hostname']

    def ip(self):
        """ Returns the ip address of the node
        
        Returns:
            str -- ip address
        """
        self.state.check('actions', 'install', 'ok')

        return self.data['ip']
    
    def power_on(self):
        """ Powers on host
        """
        self.state.check('actions', 'install', 'ok')

        self._zeroboot.port_power_on(self.data['racktivityPort'], self._racktivity, self._powermodule_id)
        self.data['powerState'] = True

    def power_off(self):
        """ Powers off host
        """
        self.state.check('actions', 'install', 'ok')
        
        self._zeroboot.port_power_off(self.data['racktivityPort'], self._racktivity, self._powermodule_id)
        self.data['powerState'] = False

    def power_cycle(self):
        """ Power cycles host
        """
        self.state.check('actions', 'install', 'ok')
        
        self._zeroboot.port_power_cycle([self.data['racktivityPort']], self._racktivity, self._powermodule_id)
        # power cycle always ends with a turned on machine
        self.data['powerState'] = True

    def power_status(self):
        """ Power state of host
        
        Returns:
            bool -- True if on, False if off
        """
        self.state.check('actions', 'install', 'ok')

        return self._zeroboot.port_info(self.data['racktivityPort'], self._racktivity, self._powermodule_id)[1]

    def monitor(self):
        """Checks if the power status of the host is the same as the last called power_on/power_off action
        If the state does not match, the last power state set trough an action will be set on the host.
        """
        self.state.check('actions', 'install', 'ok')

        if self.data['powerState'] != self.power_status():
            self.logger.debug('power state did not match')
            if self.data['powerState']:
                self.logger.debug('powering on host to match internal saved power state')
                self.power_on()
            else:
                self.logger.debug('powering off host to match internally saved power state')
                self.power_off()

    def configure_ipxe_boot(self, lkrn_url):
        """ Configure the IPXE boot settings of the host
        
        Arguments:
            lkrn_url str -- URL that points to a LKRN file to boot from that includes boot parameters. E.g.: https://bootstrap.gig.tech/krn/master/0/
        """
        self.state.check('actions', 'install', 'ok')

        if lkrn_url == self.data['lkrnUrl']:
            return

        self._host.configure_ipxe_boot(lkrn_url)
        self.data['lkrnUrl'] = lkrn_url
