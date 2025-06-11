from auth_afip import get_afip_access_ticket
from invoice_client_afip import AfipInvoiceClient, WSFE_URL_HOMO as CLIENT_WSFE_URL_HOMO
import os

# Define placeholder file paths for WSAA
CERT_PATH = "homo_certificado.crt"
KEY_PATH = "homo_clave.key"

# AFIP Web Service to access via WSAA
WSAA_SERVICE_NAME = "wsfe"

# WSAA URL for homologation (testing)
WSAA_URL_HOMO = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"

# Directory to cache tickets and WSDLs
CACHE_DIR = "/tmp/pyafipws_cache"

# Placeholder CUIT for AfipInvoiceClient
CLIENT_CUIT = "20000000000" # Use a string for CUIT

if __name__ == "__main__":
    print("--- WSAA Authentication Step ---")
    print(f"Attempting to get AFIP access ticket for service: {WSAA_SERVICE_NAME}")
    print(f"Using cert: {os.path.abspath(CERT_PATH)}")
    print(f"Using key: {os.path.abspath(KEY_PATH)}")
    print(f"Using WSAA URL: {WSAA_URL_HOMO}")
    print(f"Using cache directory: {CACHE_DIR}")

    # Create cache directory if it doesn't exist
    if CACHE_DIR and not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
            print(f"Cache directory created: {CACHE_DIR}")
        except OSError as e:
            print(f"Error creating cache directory {CACHE_DIR}: {e}")
            pass # Continue, caching might fail

    auth_token, auth_sign = get_afip_access_ticket(
        service_name=WSAA_SERVICE_NAME,
        cert_path=CERT_PATH,
        key_path=KEY_PATH,
        wsaa_url=WSAA_URL_HOMO,
        cache_dir=CACHE_DIR
    )

    if auth_token and auth_sign:
        print("\nWSAA Authentication Successful (unexpected with dummy certs).")
        print(f"Token: {auth_token}")
        print(f"Sign: {auth_sign}")
    else:
        print("\nWSAA Authentication Failed (as expected with dummy certs).")
        # Provide placeholder token/sign to test AfipInvoiceClient structure
        print("Using placeholder Token and Sign for AfipInvoiceClient instantiation.")
        auth_token = "PLACEHOLDER_TOKEN"
        auth_sign = "PLACEHOLDER_SIGN"

    print("\n--- AFIP Invoice Client Step ---")
    if auth_token and auth_sign: # Proceed if we have some token/sign (real or placeholder)
        try:
            print(f"Initializing AfipInvoiceClient with CUIT: {CLIENT_CUIT}")
            client = AfipInvoiceClient(
                CUIT=CLIENT_CUIT,
                Token=auth_token,
                Sign=auth_sign,
                wsfe_url=CLIENT_WSFE_URL_HOMO, # Using the imported constant
                cache_dir=CACHE_DIR
            )
            print("AfipInvoiceClient initialized.")

            # Test service status
            status = client.check_service_status()
            print(f"Service status from client: {status}")

        except Exception as e:
            print(f"Error during AfipInvoiceClient operations: {e}")
            # If AfipInvoiceClient.__init__ fails, client variable might not be defined.
            wsfe_instance = getattr(client, 'wsfe', None) if 'client' in locals() else None
            if wsfe_instance:
                print(f"WSFEv1 Fault String: {getattr(wsfe_instance, 'FaultString', 'N/A')}")
                print(f"WSFEv1 Fault Code: {getattr(wsfe_instance, 'FaultCode', 'N/A')}")
                print(f"WSFEv1 Exception: {getattr(wsfe_instance, 'Excepcion', 'N/A')}")
                print(f"WSFEv1 Observation: {getattr(wsfe_instance, 'Obs', 'N/A')}")

    else:
        print("Skipping AFIP Invoice Client step due to missing Token/Sign from WSAA.")

    print("\nScript finished.")
