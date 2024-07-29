import json
from aiohttp import web

from app.service.auth_svc import for_all_public_methods, check_authorization
from plugins.bastiodon.app.bastiodon_svc import BastiodonService


@for_all_public_methods(check_authorization)
class BastiodonAPI:

    def __init__(self, services, bastiodon_svc: BastiodonService):
        self.services = services
        self.auth_svc = self.services.get('auth_svc')
        self.data_svc = self.services.get('data_svc')
        self.bastiodon_svc = bastiodon_svc

    async def get_qradar_rules(self, request):
        """
        This endpoint returns all QRadar rules
        """

        name = request.query.get('name', '')

        rules = await self.bastiodon_svc.get_qradar_rules(name)
        return web.json_response(rules)
    

    async def get_qradar_offences(self, request):
        """
        This endpoint returns all QRadar offences
        """
        
        offences = await self.bastiodon_svc.get_qradar_offences()
        return web.json_response(offences)
    

    async def is_offence_active(self, request):
        """
        This endpoint returns whether a QRadar offence is active for a specified rule id
        """
        
        rule_id = request.query.get('rule_id', '')
        active = await self.bastiodon_svc.is_offence_active(rule_id)
        rep = {
            "active": active
        }
        return web.json_response(rep)

    async def attack(self, request):
        """
        This endpoint launches an attack
        """
        
        data = await request.json()
        timeout = data.get('timeout', 0)
        await self.bastiodon_svc.attack(timeout)
        return web.Response()
    
    async def is_attack_running(self, request):
        """
        This endpoint returns whether an attack is running
        """
        
        running = await self.bastiodon_svc.is_attack_running()
        rep = {
            "running": running
        }
        return web.json_response(rep)
    
    async def get_attack_status(self, request):
        """
        This endpoint returns the status of an attack
        """
        
        status = await self.bastiodon_svc.get_attack_status()
        return web.json_response(status)