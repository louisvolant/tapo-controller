#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.0

import logging
from src.services.tapo_cloud_cient import TapoCloudClient
from config import CONFIG_EMAIL, CONFIG_PASSWORD


# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# python3 tapo-controller.py
# Once finished, simply desactivate the virtual environment using "deactivate"


# Pour utilisation directe du script
def main():
    client = TapoCloudClient()

    if client.login(CONFIG_EMAIL, CONFIG_PASSWORD):
        print("Connexion réussie!")
        devices = client.get_device_list()

        print("\nListe des appareils Tapo:")
        for device in devices:
            print(f"\nNom: {device.get('deviceName')}")
            print(f"Type: {device.get('deviceType')}")
            print(f"ID: {device.get('deviceId')}")
            print(f"Modèle: {device.get('model')}")
            print(f"État: {'En ligne' if device.get('status') == 1 else 'Hors ligne'}")
    else:
        print("Échec de la connexion")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()