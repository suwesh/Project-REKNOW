import msal
import requests

YOUR_EMAIL_ID = "example@domain.com"
#functions for authentication with ms graph api
def load_msgraph_apikeys():
    # get dir of common_functions.py and join to get abs path for msgraph_apikeys.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_abspath = os.path.join(current_dir, "msgraph_apikeys.json")
    with open(json_abspath, 'r', encoding='utf-8') as apif:
        data = json.load(apif)
    return data['data']
def get_access_token():
    apicreds = load_msgraph_apikeys()
    app = msal.ConfidentialClientApplication(
        apicreds['application_client_id'],
        authority = f"https://login.microsoftonline.com/{apicreds['directory_tenant_id']}",
        client_credential = apicreds['secret_value']
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise Exception(f"Token acquisition failed!: {result}")
    return result["access_token"]
