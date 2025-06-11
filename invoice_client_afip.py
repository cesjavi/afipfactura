# This file will contain the AFIP Invoice Client logic.

from pyafipws.wsfev1 import WSFEv1
# It's good practice to also import WSAA to check its attributes if needed,
# though not strictly necessary for WSFEv1 client if Token/Sign are pre-obtained.
# from pyafipws.wsaa import WSAA # Example if needed

# Homologation URL for WSFEv1 service
WSFE_URL_HOMO = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
# Production URL for WSFEv1 service (for reference)
# WSFE_URL_PROD = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"

class AfipInvoiceClient:
    def __init__(self, CUIT, Token, Sign, wsfe_url, cache_dir=None):
        """
        Initializes the AFIP Invoice Client.

        Args:
            CUIT (str): The CUIT number for authentication and operations.
            Token (str): The access token obtained from WSAA.
            Sign (str): The signature obtained from WSAA.
            wsfe_url (str): The URL for the WSFEv1 service.
            cache_dir (str, optional): Directory to cache WSDL and other data. Defaults to None.
        """
        self.cuit = CUIT
        self.token = Token
        self.sign = Sign
        self.wsfe_url = wsfe_url
        self.cache_dir = cache_dir

        self.wsfe = WSFEv1()

        # Set authentication details for the WSFEv1 object
        self.wsfe.Token = self.token
        self.wsfe.Sign = self.sign
        self.wsfe.Cuit = self.cuit # Ensure CUIT is a string

        try:
            # Connect to the WSFEv1 service
            # The Conectar method downloads the WSDL if not cached and sets up the SOAP client.
            print(f"Connecting to WSFEv1 service at {self.wsfe_url} with CUIT {self.cuit}...")
            self.wsfe.Conectar(cache=self.cache_dir, wsdl=self.wsfe_url)
            print("Successfully connected to WSFEv1.")
        except Exception as e:
            print(f"Error connecting to WSFEv1 service: {e}")
            # Optionally, re-raise or handle more gracefully
            # print(f"WSFEv1 Fault String: {getattr(self.wsfe, 'FaultString', 'N/A')}")
            # print(f"WSFEv1 Fault Code: {getattr(self.wsfe, 'FaultCode', 'N/A')}")
            raise  # Re-raise to indicate connection failure

    def check_service_status(self):
        """
        Checks the status of the AFIP electronic invoicing web services.

        Returns:
            dict: A dictionary containing the status of AppServer, DbServer, and AuthServer.
                  Example: {'AppServerStatus': 'OK', 'DbServerStatus': 'OK', 'AuthServerStatus': 'OK'}
        Raises:
            Exception: If the Dummy call to WSFEv1 fails.
        """
        print("Checking AFIP service status (WSFEv1 Dummy call)...")
        try:
            # Dummy is a simple method to check if the service is alive and responding.
            self.wsfe.Dummy() # This method updates attributes on self.wsfe directly
            status = {
                "AppServerStatus": getattr(self.wsfe, "AppServerStatus", "N/A"),
                "DbServerStatus": getattr(self.wsfe, "DbServerStatus", "N/A"),
                "AuthServerStatus": getattr(self.wsfe, "AuthServerStatus", "N/A"),
            }
            print(f"Service status: {status}")
            if self.wsfe.Excepcion:
                print(f"WSFEv1 Dummy call reported an exception: {self.wsfe.Excepcion}")
                print(f"WSFEv1 Observation: {self.wsfe.Obs}")
                raise Exception(f"WSFEv1 Dummy call failed: {self.wsfe.Excepcion} - {self.wsfe.Obs}")
            return status
        except Exception as e:
            print(f"Error calling WSFEv1 Dummy method: {e}")
            # print(f"WSFEv1 Fault String: {getattr(self.wsfe, 'FaultString', 'N/A')}")
            # print(f"WSFEv1 Fault Code: {getattr(self.wsfe, 'FaultCode', 'N/A')}")
            raise # Re-raise the exception to be handled by the caller
