from http.server import BaseHTTPRequestHandler
import json
import base64
import zlib

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                boundary = content_type.split('boundary=')[1].encode()
                parts = post_data.split(boundary)
                
                file_content = None
                for part in parts:
                    if b'filename=' in part:
                        start = part.find(b'\r\n\r\n')
                        if start != -1:
                            file_content = part[start + 4:].rstrip(b'\r\n--')
                            break
                
                if file_content:
                    code = file_content.decode('utf-8', errors='ignore')
                    compressed = zlib.compress(code.encode())
                    encoded = base64.b64encode(compressed).decode()
                    result = f"import base64,zlib\nexec(zlib.decompress(base64.b64decode('{encoded}')))"
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/x-python')
                    self.send_header('Content-Disposition', 'attachment; filename=obfuscated.py')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(result.encode())
                    return
            
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No file"}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "message": "Obfuscator API"}).encode())