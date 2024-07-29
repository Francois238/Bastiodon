import logging
import requests

class QRadarAPI:
    def __init__(self, qradar_url, qradar_token):
        self.qradar_url = qradar_url
        self.qradar_token = qradar_token

        self.log = logging.getLogger('qradar_api')


    def get_offenses(self):
        url = f"{self.qradar_url}/api/siem/offenses?fields=last_updated_time%2Crules(id),status,description"
        headers = {
            "SEC": self.qradar_token,
            "Range": "items=0-500"
        }
        response = requests.get(url, headers=headers, verify=False)
        return response.json()
    
    def get_rules(self, name=""):
        url = f"{self.qradar_url}/api/analytics/rules?fields=name%2Cid&filter=name%20ILIKE%20%22%25{name}%25%22"
        headers = {
            "SEC": self.qradar_token,
            "Range": "items=0-50"
        }
        self.log.debug(f"Getting rules from {url}")
        response = requests.get(url, headers=headers, verify=False)
        self.log.debug(f"Got response status: {response.status_code}")
        return response.json()