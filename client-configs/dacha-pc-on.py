#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import hashlib
import sys
import ssl
from dotenv import load_dotenv
import os


load_dotenv()
router_url = os.environ.get('ROUTER_URL')
login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')
mac_address = os.environ.get('MAC_ADDRESS')



#Disable strict SSL certificate checking (in case problems with KeenDNS certificate)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_auth_hash(realm, challenge):
    # Keenetic uses MD5 + SHA256 to protect password when sending
    md5 = hashlib.md5(f"{login}:{realm}:{password}".encode('utf-8')).hexdigest()
    return hashlib.sha256(f"{challenge}{md5}".encode('utf-8')).hexdigest()

def main():
    print(f"Connecting to {router_url}...")

    # Setup cookies for session
    cookie_processor = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(cookie_processor, urllib.request.HTTPSHandler(context=ctx))
    urllib.request.install_opener(opener)

    # 1. Get tokens for autorization (Realm и Challenge)
    auth_url = f"{router_url}/auth"
    req_auth_get = urllib.request.Request(auth_url)

    try:
        urllib.request.urlopen(req_auth_get)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            realm = e.headers.get('X-NDM-Realm')
            challenge = e.headers.get('X-NDM-Challenge')
            if not realm or not challenge:
                print("Error: Keenetic security headers missing.")
                sys.exit(1)
        else:
            print(f"Network error: {e.code}")
            sys.exit(1)

    # 2. Send encrypted password
    sha = get_auth_hash(realm, challenge)
    auth_data = json.dumps({"login": login, "password": sha}).encode('utf-8')
    req_auth_post = urllib.request.Request(auth_url, data=auth_data, headers={'Content-Type': 'application/json'})

    try:
        urllib.request.urlopen(req_auth_post)
    except Exception as e:
        print(f"Autorization error (wrong password?): {e}")
        sys.exit(1)

    print("Autorization successful. Sending WOL package...")

    # 3.  API Keenetic (RCI) for server to turn on
    wol_url = f"{router_url}/rci/ip/hotspot/wake"
    wol_data = json.dumps({"mac": mac_address}).encode('utf-8')
    req_wol = urllib.request.Request(wol_url, data=wol_data, headers={'Content-Type': 'application/json'})

    try:
        urllib.request.urlopen(req_wol)
        print("Wake-on-LAN command sent successfully!")
    except Exception as e:
        print(f"Error sending package: {e}")

if __name__ == "__main__":
    main()
