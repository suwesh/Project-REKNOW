import json
import requests
import io
import pdfplumber
from docx import Document
from ms_graph_api_auth import get_access_token, YOUR_EMAIL_ID

def fetch_changed_file(itemid):##only use for fetching .json files as this returns json
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/items/{itemid}/content"
    )
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    binary = res.content
    return json.loads(binary.decode("utf-8"))
def list_runfolder_files(run_folder, subfolder):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/root:/qa_root/{run_folder}/{subfolder}:/children"
    )
    res = requests.get(url, headers=headers, timeout=60)
    res.raise_for_status()
    return res.json().get("value", [])
def download_file_content(itemid):# use for fetching any file
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/items/{itemid}/content"
    )
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    return res.content
def extract_pdf_text(binary):
    fulltext = []
    with pdfplumber.open(io.BytesIO(binary)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            pagetext = page.extract_text()
            if not pagetext:
                continue
            fulltext.append(
                f"\n\n---PAGE: {page_num} ---\n\n{pagetext}"
            )
    return "\n".join(fulltext).strip()
def extract_docx_text(binary):
    doc = Document(io.BytesIO(binary))
    fulltext = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            fulltext.append(text)
    return "\n".join(fulltext).strip()
def upload_concated_inputtext_file(run_folder, content):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/root:/qa_root/{run_folder}/02_Analysis/analyst_input_concatenated.txt:/content"
    )
    res = requests.put(
        url,
        headers=headers,
        data=content.encode("utf-8"),
        timeout=60
    )
    res.raise_for_status()
def upload_plannerinput_file(run_folder, content):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/root:/qa_root/{run_folder}/03_Planning/planner_input_ragcontext.txt:/content"
    )
    res = requests.put(
        url,
        headers=headers,
        data=json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"),
        timeout=60
    )
    res.raise_for_status()
def upload_global_describe_minitxt(run_folder, content):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/root:/qa_root/{run_folder}/04_Execution/global_described.txt:/content"
    )
    minified_content = json.dumps(content, separators=(",", ":"), ensure_ascii=False)
    res = requests.put(
        url,
        headers=headers,
        data=minified_content.encode("utf-8"),
        timeout=60
    )
    res.raise_for_status()
