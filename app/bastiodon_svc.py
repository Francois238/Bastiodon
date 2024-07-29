import logging
import asyncio
import time
import os

from plugins.bastiodon.app.qradar.api import QRadarAPI

class BastiodonService:
    def __init__(self, services):
        self.services = services
        self.file_svc = services.get('file_svc')
        self.log = logging.getLogger('bastiodon_svc')

        self.qradarapi = QRadarAPI(os.environ['qradar_ip'], os.environ['qradar_token'])

        self.attack_job = None

    # Add functions here that call core services
    async def get_qradar_rules(self, name=""):
        self.log.debug('Getting QRadar rules')
        rules = self.qradarapi.get_rules(name)
        
        return rules
    

    async def get_qradar_offences(self):
        self.log.debug('Getting QRadar offences')
        offences = self.qradarapi.get_offenses()
        
        return offences
    
    async def is_offence_active(self, rule_id):
        self.log.debug(f'Checking if offence is active for rule id {rule_id}')
        offences = self.qradarapi.get_offenses()
        rule = {
            "id": int(rule_id)
        }
        
        for offence in offences:
            if rule in offence['rules']:
                if offence['status'] == 'OPEN':
                    return True
        
        return False

    async def attack(self, timeout):
        associations = [
            {
                "ability": {
                    "id": "1000",
                    "name": "Ping from admin to intranet network"
                },
                "qradar": {
                    "id": "100452",
                    "name": "ping admin-intranet"
                }
            },
            {
                "ability": {
                    "id": "10001",
                    "name": "Ssh user to intranet"
                },
                "qradar": {
                    "id": "100403",
                    "name": "Ssh user to intranet"
                }
            }
        ]
        self.attack_job = AttackJob(self, associations, timeout)
        self.attack_job.run()
    async def is_attack_running(self):
        return self.attack_job.is_running() if (self.attack_job is not None) else False
    
    async def get_attack_status(self):
        if self.attack_job is None:
            return {
                "running": False,
                "verified_associations": []
            }
        return {
            "running": self.attack_job.is_running(),
            "verified_associations": self.attack_job.verified_associations
        }
    
class AttackJob:
    """
        AttackJob is the background job that launch attacks and query the SIEM for active offences.
        The jobs turn in the event loop created by Caldera.

        The launch process is experimental, we thought that we could launch an ability, but it is more likely that we need to launch an operation.
    """
    def __init__(self, bastiodon_svc: BastiodonService, associations, timeout):
        self.bastiodon_svc = bastiodon_svc
        self.associations = associations
        self.timeout = timeout
        self.log = logging.getLogger('attack_job')

        self.start_time = None
        self.running = False

        self.associations_to_verify = []
        self.isAllAssociationsLaunched = False

        self.verified_associations = []
        self.isAllAssociationsVerified = False

        self.launch_task = None
        self.verify_task = None
    
    def run(self):
        """
        Launch the attack job and the verify job then return.
        """
        self.start_time = time.time()
        loop = asyncio.get_event_loop()
        self.log.debug("Running attack job")
        self.launch_task = loop.create_task(self.launch_associations(self.associations))
        self.verify_task = loop.create_task(self.verify_rules())
    
    def is_running(self):
        """
        return if one of the jobs is still running
        """
        return !self.launch_task.done() or !self.verify_task.done()

    async def launch_associations(self, associations):
        """
        launch all attacks in the association list one by one
        """
        for association in associations:
            await self.launch_ability(association["ability"])
            self.associations_to_verify.append(association)
        self.isAllAssociationsLaunched = True
        self.log.debug("Launching associations task finished")

    async def launch_ability(self, ability):
        """
        Launch one Caldera ability, this is a placeholder.
        """
        self.log.debug(f'Launching ability {ability}')
        await asyncio.sleep(5)
        self.log.debug(f'Ability {ability} launched')

    async def verify_rules(self):
        """
        When an attack is launched, query the SIEM for an offence triggered by this attack.

        Return when all associations are verified or when the global timeout is reached.
        """
        self.log.debug("Verifying rules")
        while True:
            # verify timeout
            if time.time() - self.start_time > self.timeout:
                self.log.debug("Attack job timeout")
                self.launch_task.cancel()
                break
            self.log.debug(f"Verifying associations : ({len(self.associations_to_verify)}) associations left to verify")
            for association in list(self.associations_to_verify):
                if await self.bastiodon_svc.is_offence_active(association["qradar"]["id"]):
                    self.log.debug(f'Association {association} verified')
                    self.verified_associations.append(association)
                    self.associations_to_verify.remove(association)
            if len(self.verified_associations) == len(self.associations):
                self.isAllRulesVerified = True
                self.log.debug("All associations verified")
                break
            # Add missing log statements here
            self.log.debug(f"Verified associations: {len(self.verified_associations)} out of {len(self.associations)}")
            self.log.debug(f"Associations left to verify: {len(self.associations_to_verify)}")
            await asyncio.sleep(5)
        self.log.debug("Verification task finished")