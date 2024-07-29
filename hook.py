from app.utility.base_world import BaseWorld
from plugins.bastiodon.app.bastiodon_gui import BastiodonGUI
from plugins.bastiodon.app.bastiodon_api import BastiodonAPI
from plugins.bastiodon.app.bastiodon_svc import BastiodonService

name = 'Bastiodon'
description = 'Launch attack and wait for an alert from QRadar corresponding to this alert'
address = '/plugin/bastiodon/gui'
# This plugin is only available for users in blue team, could be changed.
access = BaseWorld.Access.BLUE


async def enable(services):
    app = services.get('app_svc').application
    bastiodon_gui = BastiodonGUI(services, name=name, description=description)
    app.router.add_static('/bastiodon', 'plugins/bastiodon/static/', append_version=True)
    app.router.add_route('GET', '/plugin/bastiodon/gui', bastiodon_gui.splash)

    bastiodon_svc = BastiodonService(services)
    bastiodon_api = BastiodonAPI(services, bastiodon_svc)
    # Add API routes here
    app.router.add_route('GET', '/plugin/bastiodon/qradar/rules', bastiodon_api.get_qradar_rules)
    app.router.add_route('GET', '/plugin/bastiodon/qradar/offences', bastiodon_api.get_qradar_offences)
    app.router.add_route('GET', '/plugin/bastiodon/qradar/is_offence_active', bastiodon_api.is_offence_active)
    app.router.add_route('POST', '/plugin/bastiodon/attack', bastiodon_api.attack)
    app.router.add_route('GET', '/plugin/bastiodon/is_attack_running', bastiodon_api.is_attack_running)
    app.router.add_route('GET', '/plugin/bastiodon/attack', bastiodon_api.get_attack_status)
    
