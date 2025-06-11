# This file will contain the WSAA authentication logic.

# To obtain the .crt and .key files:
# 1. Generate a Certificate Signing Request (CSR) and a private key (.key) using OpenSSL.
#    Example: openssl genrsa -out private_key.key 2048
#             openssl req -new -key private_key.key -subj "/C=AR/O=YourOrganization/CN=YourCUIT" -out request.csr
# 2. Submit the CSR to the AFIP portal to obtain a signed certificate (.crt).
#    This process usually involves logging into the AFIP website with your CUIT and Clave Fiscal.
# 3. Place the generated .crt and .key files in a secure location accessible by this script.

import os
from pyafipws.wsaa import WSAA

def get_afip_access_ticket(service_name, cert_path, key_path, wsaa_url, cache_dir=None):
    """
    Authenticates with AFIP's Web Service Authorization (WSAA) and retrieves an access ticket.

    Args:
        service_name (str): The AFIP web service to access (e.g., "wsfe", "wsfex").
        cert_path (str): Path to the AFIP certificate file (.crt).
        key_path (str): Path to the private key file (.key).
        wsaa_url (str): URL of the WSAA service.
                        For testing/homologation: "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
                        For production: "https://wsaa.afip.gov.ar/ws/services/LoginCms"
        cache_dir (str, optional): Directory to cache the access ticket. Defaults to None.

    Returns:
        tuple: (token, sign) if successful, otherwise None.
    """
    if not os.path.exists(cert_path):
        print(f"Error: Certificate file not found at {cert_path}")
        return None, None
    if not os.path.exists(key_path):
        print(f"Error: Key file not found at {key_path}")
        return None, None

    wsaa = WSAA()

    try:
        # Create TRA (Ticket de Requerimiento de Acceso)
        tra = wsaa.CreateTRA(service=service_name)
        print("TRA created.")

        # Sign TRA
        cms = wsaa.SignTRA(tra, cert_path, key_path)
        print("TRA signed.")

        # Connect to WSAA and Login
        # The wsdl argument in Conectar specifies the WSAA server.
        # pyafipws defaults to the homologation (testing) server if wsdl is not provided.
        wsaa.Conectar(cache=cache_dir, wsdl=wsaa_url)
        print(f"Connected to WSAA: {wsaa_url}")

        wsaa.LoginCMS(cms)
        print("LoginCMS successful.")

        return wsaa.Token, wsaa.Sign
    except Exception as e:
        print(f"Error during AFIP WSAA authentication: {e}")
        print(f"WSAA Fault String: {getattr(wsaa, 'FaultString', 'N/A')}")
        print(f"WSAA Fault Code: {getattr(wsaa, 'FaultCode', 'N/A')}")
        return None, None
