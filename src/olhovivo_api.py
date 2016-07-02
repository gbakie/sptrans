"""
Access methods from OlhoVivo API using http requests
"""
__author__ = "gbakie"

import requests
from time import sleep

class ApiException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class OlhoVivoAPI(object):

    VERSION = 0
    BASE_URL = 'http://api.olhovivo.sptrans.com.br/v%d' % 0

    # path in the url from the methods accessed
    AUTH_PATH = '/Login/Autenticar?token=%s'
    SEARCH_PATH = '/Linha/Buscar'
    POS_PATH = '/Posicao'

    # http get method parameters
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
            return None

        params = {self.SEARCH_PARAM: route_id}
        url = self.BASE_URL + self.SEARCH_PATH
        return self._get_method(url, params)
        

    def get_bus_pos(self, bus_code):
        if self.auth == False:
            print "Not authenticated" 
            return None

        params = {self.POS_PARAM: bus_code}
        url = self.BASE_URL + self.POS_PATH
        return self._get_method(url, params)

    def _get_method(self, url, params):
        r_ok = False

        for i in range(self.max_retries):
            try:
                r = requests.get(url, params=params, 
                                cookies=self.cookies, timeout=self.timeout)

                if r.status_code == 200:
                    r_ok = True
                    content = r.json()
                    break
                elif r.status_code == 401:
                    # Try to authenticate again
                    self.auth = False
                    if not self.authenticate():
                        break
                        
            except requests.exceptions.RequestException as e:
                # DEBUG
                print "connection error" + str(e)
                sleep(self.time_retry)
            except TypeError as e:
                print "Could not parse content from request"
                print str(e)
                return None

        # could not get the resources
        if r_ok == False:
            self.auth = False
            return None
        
        return content
