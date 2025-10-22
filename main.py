from auth_afip import get_afip_access_ticket
from invoice_client_afip import AfipInvoiceClient, WSFE_URL_HOMO as CLIENT_WSFE_URL_HOMO
import os
import textwrap

# --- Configuration ---
# TODO: Replace these placeholders with your actual CUIT and file paths.
# You can get your certificate (.crt) and private key (.key) from the AFIP portal.
CERT_PATH = "homo_certificado.crt"
KEY_PATH = "homo_clave.key"
CLIENT_CUIT = "20000000000"  # Your CUIT goes here as a string

# AFIP Web Service details (no need to change for testing)
WSAA_SERVICE_NAME = "wsfe"
WSAA_URL_HOMO = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
CACHE_DIR = "/tmp/pyafipws_cache"

def print_centered_header(text, width=80):
    """Prints a centered header."""
    print("\n" + text.center(width, "=") + "\n")

if __name__ == "__main__":
    print_centered_header("AFIP Web Service Client Example")

    # --- Step 1: WSAA Authentication ---
    print_centered_header("Step 1: WSAA Authentication")

    print("This script will attempt to authenticate with AFIP's WSAA service.")
    print(f"  - Service: {WSAA_SERVICE_NAME}")
    print(f"  - Cert Path: {os.path.abspath(CERT_PATH)}")
    print(f"  - Key Path: {os.path.abspath(KEY_PATH)}")

    # Create cache directory if it doesn't exist
    if CACHE_DIR and not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
            print(f"Cache directory created at: {CACHE_DIR}")
        except OSError as e:
            print(f"Warning: Could not create cache directory {CACHE_DIR}: {e}")

    auth_token, auth_sign = get_afip_access_ticket(
        service_name=WSAA_SERVICE_NAME,
        cert_path=CERT_PATH,
        key_path=KEY_PATH,
        wsaa_url=WSAA_URL_HOMO,
        cache_dir=CACHE_DIR
    )

    use_real_auth = True
    if not (auth_token and auth_sign):
        use_real_auth = False
        print("\nWARNING: WSAA Authentication Failed (as expected with dummy certs).")
        print("The script will proceed with placeholder credentials for demonstration purposes.")
        print("However, most AFIP service calls will fail without a valid token.")
        print("-" * 80)
        print("ACTION REQUIRED:")
        print("1. Replace 'homo_certificado.crt' and 'homo_clave.key' with your actual files.")
        print(f"2. Set 'CLIENT_CUIT' to your CUIT ({CLIENT_CUIT} is a placeholder).")
        print("-" * 80)
        # Provide placeholder token/sign to test AfipInvoiceClient structure
        auth_token = "PLACEHOLDER_TOKEN"
        auth_sign = "PLACEHOLDER_SIGN"
    else:
        print("\nSUCCESS: WSAA Authentication successful.")
        print(f"  - Token: {textwrap.shorten(auth_token, width=50, placeholder='...')}")
        print(f"  - Sign: {textwrap.shorten(auth_sign, width=50, placeholder='...')}")

    # --- Step 2: AFIP Invoice Client Operations ---
    print_centered_header("Step 2: AFIP Service Interaction")

    try:
        print(f"Initializing AfipInvoiceClient for CUIT: {CLIENT_CUIT}")
        client = AfipInvoiceClient(
            CUIT=CLIENT_CUIT,
            Token=auth_token,
            Sign=auth_sign,
            wsfe_url=CLIENT_WSFE_URL_HOMO,
            cache_dir=CACHE_DIR
        )
        print("Client initialized successfully.")

        # --- Example Call 1: Check Service Status ---
        print("\n--- Example Call 1: Check Service Status ---")
        status = client.check_service_status()
        print(f"Service status: {status}")

        # --- Example Call 2: Get Voucher Types ---
        # This call will fail with placeholder credentials.
        print("\n--- Example Call 2: Get Available Voucher Types ---")
        if not use_real_auth:
            print("Skipping this call because it requires valid authentication.")
            print("With placeholder credentials, it would fail with an 'Invalid Token/Sign' error.")
        else:
            voucher_types = client.get_voucher_types()
            print("Available Voucher Types:")
            if voucher_types:
                # Print in a readable table format
                print(f"{'ID':<5} | {'Description':<30} | {'Valid From':<12} | {'Valid To':<12}")
                print("-" * 65)
                for v_type in voucher_types:
                    print(f"{v_type['Id']:<5} | {v_type['Desc']:<30} | {v_type['FchDesde']:<12} | {v_type['FchHasta']:<12}")
            else:
                print("No voucher types found or an error occurred.")

    except Exception as e:
        print(f"\nERROR: An error occurred during AFIP client operations: {e}")
        # Detailed error info from the soap client, if available
        wsfe_instance = getattr(client, 'wsfe', None) if 'client' in locals() else None
        if wsfe_instance:
            print("Detailed SOAP Error Information:")
            print(f"  - Fault String: {getattr(wsfe_instance, 'FaultString', 'N/A')}")
            print(f"  - Fault Code: {getattr(wsfe_instance, 'FaultCode', 'N/A')}")
            print(f"  - Exception: {getattr(wsfe_instance, 'Excepcion', 'N/A')}")
            print(f"  - Observation: {getattr(wsfe_instance, 'Obs', 'N/A')}")

    print_centered_header("Script Finished", width=80)
