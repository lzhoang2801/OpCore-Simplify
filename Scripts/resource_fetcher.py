import sys
import ssl
import os
import plistlib
import json

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
else:
    import urllib2
    from urllib2 import urlopen, Request

class ResourceFetcher:
    def __init__(self, headers=None):
        self.request_headers = headers
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

    def fetch_and_parse_content(self, resource_url, content_type=None):
        request = Request(resource_url, headers=self.request_headers or {})
        with urlopen(request, context=self.ssl_context) as response:
            content = response.read()
            if content_type == 'json':
                return json.loads(content)
            elif content_type == 'plist':
                return plistlib.loads(content)
            else:
                return content.decode('utf-8')

    def download_and_save_file(self, resource_url, destination_path):
        request = Request(resource_url, headers=self.request_headers or {})
        with urlopen(request, context=self.ssl_context) as response:
            total_size = response.length
            bytes_downloaded = 0
            print("Download from {}".format(resource_url))

            with open(destination_path, 'wb') as file_writer:
                while True:
                    chunk = response.read(self.buffer_size)
                    if not chunk:
                        break
                    file_writer.write(chunk)
                    bytes_downloaded += len(chunk)
                    if total_size:
                        print("Downloaded {:.2f} MB of {:.2f} MB".format(bytes_downloaded / (1024 * 1024), total_size / (1024 * 1024)), end='\r')
