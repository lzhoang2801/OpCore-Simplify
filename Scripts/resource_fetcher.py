import ssl
import os
import json
import plistlib
import socket
import sys
import gzip
import zlib
import time

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
    from urllib.error import URLError
else:
    import urllib2
    from urllib2 import urlopen, Request, URLError

class ResourceFetcher:
    def __init__(self, headers=None):
        self.request_headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
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
            print("Failed to create SSL context: {}".format(e))
            ssl_context = ssl._create_unverified_context()
        return ssl_context

    def _make_request(self, resource_url, timeout=10):
        try:
            headers = dict(self.request_headers)
            headers["Accept-Encoding"] = "gzip, deflate"
            
            return urlopen(Request(resource_url, headers=headers), timeout=timeout, context=self.ssl_context)
        except socket.timeout as e:
            print("Timeout error: {}".format(e))
        except ssl.SSLError as e:
            print("SSL error: {}".format(e))
        except (URLError, socket.gaierror) as e:
            print("Connection error: {}".format(e))
        except Exception as e:
            print("Request failed: {}".format(e))

        return None

    def fetch_and_parse_content(self, resource_url, content_type=None):
        attempt = 0
        response = None

        while attempt < 3:
            response = self._make_request(resource_url)

            if not response:
                attempt += 1
                print("Failed to fetch content from {}. Retrying...".format(resource_url))
                continue

            if response.getcode() == 200:
                break

            attempt += 1

        if not response:
            print("Failed to fetch content from {}".format(resource_url))
            return None
        
        content = response.read()

        if response.info().get("Content-Encoding") == "gzip" or content.startswith(b"\x1f\x8b"):
            try:
                content = gzip.decompress(content)
            except Exception as e:
                print("Failed to decompress gzip content: {}".format(e))
        elif response.info().get("Content-Encoding") == "deflate":
            try:
                content = zlib.decompress(content)
            except Exception as e:
                print("Failed to decompress deflate content: {}".format(e))
        
        try:
            if content_type == "json":
                return json.loads(content)
            elif content_type == "plist":
                return plistlib.loads(content)
            else:
                return content.decode("utf-8")
        except Exception as e:
            print("Error parsing content as {}: {}".format(content_type, e))
            
        return None

    def _download_with_progress(self, response, local_file):
        total_size = response.getheader("Content-Length")
        if total_size:
            total_size = int(total_size)
        bytes_downloaded = 0
        start_time = time.time()
        last_time = start_time
        last_bytes = 0
        speeds = []

        speed_str = "-- KB/s"
        
        while True:
            chunk = response.read(self.buffer_size)
            if not chunk:
                break
            local_file.write(chunk)
            bytes_downloaded += len(chunk)
            
            current_time = time.time()
            time_diff = current_time - last_time
            
            if time_diff > 0.5:
                current_speed = (bytes_downloaded - last_bytes) / time_diff
                speeds.append(current_speed)
                if len(speeds) > 5:
                    speeds.pop(0)
                avg_speed = sum(speeds) / len(speeds)
                
                if avg_speed < 1024*1024:
                    speed_str = "{:.1f} KB/s".format(avg_speed/1024)
                else:
                    speed_str = "{:.1f} MB/s".format(avg_speed/(1024*1024))
                
                last_time = current_time
                last_bytes = bytes_downloaded
            
            if total_size:
                percent = int(bytes_downloaded / total_size * 100)
                bar_length = 40
                filled = int(bar_length * bytes_downloaded / total_size)
                bar = "█" * filled + "░" * (bar_length - filled)
                progress = "{} [{}] {:3d}% {:.1f}/{:.1f}MB".format(speed_str, bar, percent, bytes_downloaded/(1024*1024), total_size/(1024*1024))
            else:
                progress = "{} {:.1f}MB downloaded".format(speed_str, bytes_downloaded/(1024*1024))
            
            print(" " * 80, end="\r")
            print(progress, end="\r")
            
        print()

    def download_and_save_file(self, resource_url, destination_path):
        attempt = 0

        while attempt < 3:
            response = self._make_request(resource_url)

            if not response:
                attempt += 1
                print("Failed to download file from {}. Retrying...".format(resource_url))
                continue

            self._download_with_progress(response, open(destination_path, "wb"))

            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                return True
            
            attempt += 1

        return False