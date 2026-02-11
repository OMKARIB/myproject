#!/usr/bin/env python3
# client.py
import re
import sys
import xml.etree.ElementTree as ET
from urllib import request, error

SERVER_URL = "http://127.0.0.1:8000/api"

def validate(name: str, email: str, idv: str) -> tuple[bool, str]:
    name = (name or "").strip()
    email = (email or "").strip()
    idv = (idv or "").strip()

    if not name:
        return False, "Name is required."
    # Allow letters/spaces/dot/hyphen/apostrophe; adjust as needed
    if not re.fullmatch(r"[A-Za-z][A-Za-z\s.\-']{0,99}", name):
        return False, "Name contains invalid characters or is too long."

    if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        return False, "Email format is invalid."

    if not idv.isdigit():
        return False, "ID must be numeric."

    return True, "OK"

def build_xml(name: str, email: str, idv: str) -> bytes:
    root = ET.Element("KPIT")
    ET.SubElement(root, "Name").text = name
    ET.SubElement(root, "Email").text = email
    ET.SubElement(root, "ID").text = idv
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def send(xml_payload: bytes) -> tuple[int, str]:
    req = request.Request(
        SERVER_URL,
        data=xml_payload,
        headers={"Content-Type": "application/xml; charset=utf-8"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as he:
        return he.code, he.read().decode("utf-8", errors="replace")
    except error.URLError as ue:
        return 0, f"Network error: {ue.reason}"
    except Exception as e:
        return 0, f"Unexpected error: {e}"

def main():
    print("Enter details to send to server:")
    name = input("Name : ").strip()
    email = input("Email: ").strip()
    idv = input("ID   : ").strip()

    ok, msg = validate(name, email, idv)
    if not ok:
        print("❌ Validation failed:", msg)
        sys.exit(1)

    payload = build_xml(name, email, idv)
    status, body = send(payload)
    if status == 200:
        print("✅ Success:", body)
    elif status == 0:
        print("❌", body)
    else:
        print(f"❌ HTTP {status}: {body}")

if __name__ == "__main__":
    main()
