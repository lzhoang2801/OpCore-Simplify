import requests
import ssl
import os
import certifi
import plistlib

class ResourceFetcher:
    def __init__(self, headers = None):
        self.request_headers = headers
        self.buffer_size = 16*1024
        self.ssl_context = self.create_ssl_context()

    def create_ssl_context(self):
        try:
            cafile = ssl.get_default_verify_paths().openssl_cafile
            if not os.path.exists(cafile):
                cafile = certifi.where()
            ssl_context = ssl.create_default_context(cafile=cafile)
        except Exception as e:
            print(f"SSL Context Creation Error: {e}")
            ssl_context = ssl._create_unverified_context()
        return ssl_context

    def fetch_and_parse_content(self, resource_url, content_type=None):
        response = requests.get(resource_url, headers=self.request_headers, verify=self.ssl_context.verify_mode != ssl.CERT_NONE)
        response.raise_for_status()

        if content_type == 'json':
            return response.json()
        elif content_type == 'plist':
            return plistlib.loads(response.content)
        else:
            return response.text

    def download_and_save_file(self, resource_url, destination_path, extract=True):
        with requests.get(resource_url, headers=self.request_headers, stream=True, verify=self.ssl_context.verify_mode != ssl.CERT_NONE) as response:
            response.raise_for_status()

            try:
                total_size = int(response.headers.get('Content-Length', -1))
            except ValueError:
                total_size = -1
            
            bytes_downloaded = 0
            
            print(f"Download from {resource_url}")
            
            with open(destination_path, 'wb') as file_writer:
                while True:
                    chunk = response.raw.read(self.buffer_size)
                    if not chunk:
                        break
                    file_writer.write(chunk)
                    bytes_downloaded += len(chunk)
                    if total_size != -1:
                        print(f"Downloaded {bytes_downloaded / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB", end='\r')