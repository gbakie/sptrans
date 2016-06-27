"""
Access methods from OlhoVivo API using http requests
"""
__author__ = "gbakie"

import requests
from time import sleep

class OlhoVivoAPI(object):

    VERSION = 0
    BASE_URL = 'http://api.olhovivo.sptrans.com.br/v%d' % 0
    AUTH_PATH = '/Login/Autenticar?token=%s'
    SEARCH_PATH = '/Linha/Buscar'
    POS_PATH = '/Posicao'

    SEARCH_PARAM = 'termosBusca'
    POS_PARAM = 'codigoLinha'
    

    def __init__(self, key, max_retries=3, timeout=0.5, time_retry=0.5):
        self.key = key
        self.cookies = None
        self.auth = False
        self.max_retries = max_retries
        self.timeout = timeout
        self.time_retry = time_retry


    def authenticate(self):
        auth_path = self.AUTH_PATH % self.key
        url = self.BASE_URL + auth_path

        try:
            r = requests.post(url)
        except requests.exceptions.RequestException as e:
            # DEBUG
            print str(e)
            return False

        # check for negative response
        if r.text != 'true':
            return False

        self.cookies = r.cookies
        self.auth = True

        return True


    def get_bus_info(self, route_id):
        if self.auth == False:
            print "Not authenticated" 
            return []

        search_params = {self.SEARCH_PARAM: route_id}
        url = self.BASE_URL + self.SEARCH_PATH
        try:
            r = requests.get(url, params=search_params, cookies=self.cookies)
        except requests.exceptions.RequestException as e:
            # DEBUG
            print str(e)
            return []
        
        # TODO check error in the text
        try:
            content = r.json()
        except:
            print "Could not parse content from request"
            print content
            return []
        
        return content
        

    def get_bus_pos(self, bus_code):
        if self.auth == False:
            print "Not authenticated" 
            return None

        pos_params = {self.POS_PARAM: bus_code}
        url = self.BASE_URL + self.POS_PATH
        n_tries = 0

        while n_tries < self.max_retries:
            try:
                r = requests.get(url, params=pos_params, 
                                cookies=self.cookies, timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                # DEBUG
                print "connection error" + str(e)
                n_tries += 1
                sleep(self.time_retry)
                continue

            if r.status_code == 200:
                break
            elif r.status_code == 401:
                self.auth = False
                self.authenticate()
                n_tries += 1

        if n_tries >= self.max_retries:
            self.auth = False
            return None

        try:
            content = r.json()
        except:
            # DEBUG
            print "Could not parse content from request"
            print content
            return None
        
        return content

