from config import SRAM_API_KEY, SRAM_API_ROOT, DATA_DIR
import requests
from requests_cache import CachedSession
import json
import logging
import pandas as pd
import time
from datetime import datetime, timedelta

logger = logging.getLogger('sram_tasks')
# cache for 8 hours for easier testing
session = CachedSession(cache_name="sram_requests_cache", allowable_methods=("GET", "POST"), expire_after=timedelta(hours=8))

def handle_exception():
    logger.warning('script failed with an error')
    raise SystemExit(0)

class SramData():
    def __init__(self):
        self.orgdata = {}
        self.users = {}
    
    def _store(self, filename, data):
        """
        Store the data dict as a json file

        :param data: dict
        :param filename: string
        :return:
        """
        with open(filename, "w") as f:
            json.dump(data, f, indent=1)

    def _do_sram_getrequest(self, url):
        headers = {"Authorization": f"Bearer {SRAM_API_KEY}", "Accept": "application/json"}
        res = session.get(url, headers=headers)
        if session.cache.contains(url=url):
            cached = True
        else: 
            time.sleep(5) # sleep for 1 second to avoid rate limiting
        if res.status_code == 200:
            return res, cached
        else:
            return False, False
            #raise Exception("*** Got: status_code: %s" % res.status_code)
    
    def get_sram_organization(self):
        res, cached = self._do_sram_getrequest(f"{SRAM_API_ROOT}/api/organisations/v1")
        data = json.loads(res.content)
        return data
    
    def get_invitation(self, co_identifier):
        res, cached = self._do_sram_getrequest(
            f"{SRAM_API_ROOT}/api/invitations/v1/invitations/{co_identifier}"
        )
        try:    
            data = json.loads(res.content)
            
        except:
            return None, cached
        return data, cached
    
    def get_co_details(self, co_identifier):
        res, cached = self._do_sram_getrequest(
            f"{SRAM_API_ROOT}/api/collaborations/v1/{co_identifier}"
        )
        try:
            data = json.loads(res.content)
        except:
            return None, cached
        return data, cached
            
    
    def get_sram_open_invitations(self):
        invitations = {}
        for co in self.orgdata["collaborations"]:
            
            data, cached = self.get_invitation(co["identifier"])
            if data is not None:
                invitations[co["identifier"]] = data
                self._store(filename=f'{DATA_DIR}/dump/{co["identifier"]}_invitations.json', data=data)
        return invitations
    
    def get_sram_details(self):
        details = {}
        for co in self.orgdata["collaborations"]:
            data, cached = self.get_co_details(co["identifier"])
            details[co["identifier"]] = data
            self._store(filename=f'{DATA_DIR}/dump/{co["identifier"]}_details.json', data=data)
        return details
    
    def collect(self):
        self.orgdata = self.get_sram_organization()
        self.invitations = self.get_sram_open_invitations()
        self.details = self.get_sram_details()
        
        self.users = {}
        # per email address get invitations and memberships counts
        for co_id, data in self.invitations.items():
            for invitation in data:
                email = invitation["invitation"]["email"]
                if email not in self.users:
                    self.users[email] = {"invitations": 0, "memberships": 0}
                self.users[email]["invitations"] += 1

        for co_id, data in self.details.items():
            for member in data["collaboration_memberships"]:
                email = member["user"]["email"]
                if email not in self.users:
                    self.users[email] = {"invitations": 0, "memberships": 0}
                self.users[email]["memberships"] += 1
        
        self.collaborations = {}
        for co in self.orgdata["collaborations"]:
            self.collaborations[co["identifier"]]={}
            self.collaborations[co["identifier"]]["name"] = co["name"]
            self.collaborations[co["identifier"]]["membership_count"] = co["collaboration_memberships_count"]
            invitation_count = 0	
            for invitation in self.invitations[co["identifier"]]:
                if invitation["status"] == "open":
                    invitation_count += 1
            self.collaborations[co["identifier"]]["invitation_count"] = invitation_count
        


