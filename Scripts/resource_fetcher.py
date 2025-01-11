import ssl
import os
import json
import plistlib
import socket
import sys

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
else:
    import urllib2
    from urllib2 import urlopen, Request

class ResourceFetcher:
    def __init__(self, headers=None):
        self.request_headers = headers or {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        self.buffer_size = 16 * 1024
        self.ssl_context = self.create_ssl_context()

    def create_ssl_context(self):
        try:
            cafile = ssl.get_default_verify_paths().openssl_cafile
            if not os.path.exists(cafile):
                import certifi
                cafile = certifi.where()
            ssl_context = ssl.create_default_context(cafile=cafile)
        except Exception as e:
            print("SSL Context Creation Error: {}".format(e))
            ssl_context = ssl._create_unverified_context()
        return ssl_context

    def is_connected(self, timeout=5):
        socket.create_connection(("github.com", 443), timeout=timeout)

    def _make_request(self, resource_url):
        self.is_connected()

        try:
            return urlopen(Request(resource_url, headers=self.request_headers), context=self.ssl_context)
        except Exception as e:
            pass

        return None

    def fetch_and_parse_content(self, resource_url, content_type=None):
        response = self._make_request(resource_url)

        if not response:
            return None
        
        content = response.read()
        if content_type == 'json':
            return json.loads(content)
        elif content_type == 'plist':
            return plistlib.loads(content)
        else:
            return content.decode('utf-8')

    def _download_with_progress(self, response, local_file):
        total_size = response.getheader('Content-Length')
        if total_size:
            total_size = int(total_size)
        bytes_downloaded = 0

        while True:
            chunk = response.read(self.buffer_size)
            if not chunk:
                break
            local_file.write(chunk)
            bytes_downloaded += len(chunk)

            if total_size:
                percent = int(bytes_downloaded / total_size * 100)
                progress = f"[{'=' * (percent // 2):50s}] {percent}%  {bytes_downloaded / (1024 * 1024):.2f}/{total_size / (1024 * 1024):.2f} MB"
            else:
                progress = f"Downloaded {bytes_downloaded / (1024 * 1024):.2f} MB"
            print(progress, end='\r')

        print()

    def download_and_save_file(self, resource_url, destination_path):
        response = self._make_request(resource_url)

        if not response:
            return None

        with open(destination_path, 'wb') as local_file:
            print(f"Downloading from {resource_url}")
            self._download_with_progress(response, local_file)