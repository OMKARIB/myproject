from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
from pathlib import Path

FILE = Path("records.xml")

def indent(e, lvl=0):
    i = "\n" + lvl * "  "
    if len(e):
        if not e.text or not e.text.strip(): e.text = i + "  "
        for c in e: indent(c, lvl + 1)
    if lvl and (not e.tail or not e.tail.strip()): e.tail = i

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api": return self.send_error(404)
        ln = int(self.headers.get("Content-Length", 0))
        if ln == 0: return self.send_error(400, "Empty")
        try: root = ET.fromstring(self.rfile.read(ln))
        except: return self.send_error(400, "Bad XML")
        name, email, idv = map(lambda x: root.findtext(x), ("Name","Email","ID"))
        if not (name and email and idv.isdigit()): return self.send_error(400,"Invalid")
        if FILE.exists(): tree = ET.parse(FILE); r = tree.getroot()
        else: r = ET.Element("KPITRecords"); tree = ET.ElementTree(r)
        rec = ET.SubElement(r, "KPIT")
        for t,v in (("Name",name),("Email",email),("ID",idv)): ET.SubElement(rec,t).text=v
        indent(r); tree.write(FILE, encoding="utf-8", xml_declaration=True)
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
