import logging
import requests
import hashlib
import json
import uuid
import time
import urllib3
import base64
import hmac
from urllib.parse import quote, urlencode


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TapoCloudClient:
    def __init__(self):
        self.base_url = "https://n-euw1-wap-gw.tplinkcloud.com"
        self.session = requests.Session()
        self.session.verify = False
        self.token = None
        self.key = "Tp-Link_Kasa_Android2.0"  # Nouvelle clé avec version

    def _hash_password(self, password):
        return hashlib.sha1(password.encode()).hexdigest()

    def _generate_signature(self, params):
        """Génère la signature selon une nouvelle méthode"""
        # Trie les paramètres par clé
        sorted_params = dict(sorted(params.items()))

        # Encode chaque valeur individuellement
        encoded_params = {k: quote(str(v), safe='') for k, v in sorted_params.items()}

        # Construit la chaîne à signer
        string_to_sign = urlencode(encoded_params, safe='')

        # Encode la chaîne en base64
        base64_string = base64.b64encode(string_to_sign.encode()).decode()

        # Crée un nouveau HMAC avec la clé et le base64
        hmac_obj = hmac.new(
            self.key.encode(),
            base64_string.encode(),
            hashlib.sha256
        )

        # Retourne la signature finale
        signature = hmac_obj.hexdigest()

        logging.debug(f"Original params: {params}")
        logging.debug(f"Encoded params: {encoded_params}")
        logging.debug(f"String to sign: {string_to_sign}")
        logging.debug(f"Base64 string: {base64_string}")
        logging.debug(f"Final signature: {signature}")

        return signature, string_to_sign

    def login(self, email, password):
        endpoint = "/api/v2/account/login"

        # Ajout de paramètres supplémentaires
        params = {
            "appType": "Tapo_Android",
            "cloudPassword": self._hash_password(password),
            "cloudUserName": email,
            "terminalUUID": str(uuid.uuid4()),
            "timestamp": str(int(time.time() * 1000)),
            "locale": "fr_FR",
            "platform": "Android",
            "model": "SDK_30"
        }

        signature, string_to_sign = self._generate_signature(params)
        params["signature"] = signature

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Tapo/2.1.14 (Android, 30)",
            "requestByApp": "true",
            "Accept-Language": "fr-FR",
            "X-Platform": "Android",
            "Connection": "Keep-Alive"
        }

        try:
            logging.info("Tentative de connexion à l'API Tapo...")
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=params,
                headers=headers
            )
            response.raise_for_status()

            result = response.json()
            if result.get("error_code") == 0:
                self.token = result["result"]["token"]
                logging.info("Connexion réussie!")
                return True
            else:
                logging.error(f"Erreur de connexion: {result.get('msg', 'Erreur inconnue')}")
                logging.error(f"Code d'erreur: {result.get('error_code')}")
                logging.debug(f"Paramètres envoyés: {json.dumps(params, indent=2)}")
                return False

        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors de la requête: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Détails de l'erreur: {e.response.text}")
            return False

    def get_device_list(self):
        """Récupère la liste des appareils associés au compte"""
        if not self.token:
            logging.error("Vous devez d'abord vous connecter")
            return []

        endpoint = "/api/v2/device/list"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "requestByApp": "true",
            "User-Agent": "Tapo/2.1.14 (Android, 30)"
        }

        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json={}
            )
            response.raise_for_status()

            result = response.json()
            if result.get("error_code") == 0:
                return result["result"]["deviceList"]
            else:
                logging.error(f"Erreur lors de la récupération des appareils: {result.get('msg', 'Erreur inconnue')}")
                logging.error(f"Code d'erreur: {result.get('error_code')}")
                return []

        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors de la requête: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Détails de l'erreur: {e.response.text}")
            return []
