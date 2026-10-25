import hashlib
import ssl
import os
import json
import plistlib
import socket
import sys
import gzip
import zlib
import time
from functools import lru_cache

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
    from urllib.error import URLError
else:
    import urllib2
    from urllib2 import urlopen, Request, URLError

MAX_ATTEMPTS = 3


@lru_cache(maxsize=1)
def get_ssl_context():
    context = ssl.create_default_context()
    try:
        import certifi
    except ModuleNotFoundError as error:
        if error.name != "certifi":
            raise
        return context
    context.load_verify_locations(cafile=certifi.where())
    return context


class ResourceFetcher:
    def __init__(self, headers=None):
        self.request_headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.buffer_size = 16 * 1024

    def _make_request(self, resource_url, timeout=10):
        try:
            headers = dict(self.request_headers)
            headers["Accept-Encoding"] = "gzip, deflate"
            
            return urlopen(Request(resource_url, headers=headers), timeout=timeout, context=get_ssl_context())
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
        sha256 = hashlib.sha256()
        show_progress = sys.stdout.isatty()
        total_size = response.getheader("Content-Length")
        if total_size:
            total_size = int(total_size)
        bytes_downloaded = 0
        last_time = time.monotonic()
        last_progress = last_time
        last_bytes = 0
        speeds = []

        speed_str = "-- KB/s"
        
        while True:
            chunk = response.read(self.buffer_size)
            if not chunk:
                break
            local_file.write(chunk)
            sha256.update(chunk)
            bytes_downloaded += len(chunk)
            
            if not show_progress:
                continue
            current_time = time.monotonic()
            if current_time - last_progress < 0.1 and bytes_downloaded != total_size:
                continue
            last_progress = current_time
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
                bar = "#" * filled + "-" * (bar_length - filled)
                progress = "{} [{}] {:3d}% {:.1f}/{:.1f}MB".format(speed_str, bar, percent, bytes_downloaded/(1024*1024), total_size/(1024*1024))
            else:
                progress = "{} {:.1f}MB downloaded".format(speed_str, bytes_downloaded/(1024*1024))
            
            print(progress.ljust(80), end="\r", flush=True)
            
        if show_progress:
            print()
        return sha256.hexdigest()

    def download_and_save_file(self, resource_url, destination_path, sha256_hash=None):
        attempt = 0

        while attempt < MAX_ATTEMPTS:
            attempt += 1
            response = self._make_request(resource_url)

            if not response:
                print("Failed to fetch content from {}. Retrying...".format(resource_url))
                continue

            with open(destination_path, "wb") as local_file:
                downloaded_hash = self._download_with_progress(response, local_file)

            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                if sha256_hash:
                    print("Verifying SHA256 checksum...")
                    if downloaded_hash.lower() == sha256_hash.lower():
                        print("Checksum verified successfully.")
                        return True
                    else:
                        print("Checksum mismatch! Removing file and retrying download...")
                        os.remove(destination_path)
                        continue
                else:
                    print("No SHA256 hash provided. Downloading file without verification.")
                    return True
            
            if os.path.exists(destination_path):
                os.remove(destination_path)

            if attempt < MAX_ATTEMPTS:
                print("Download failed for {}. Retrying...".format(resource_url))

        print("Failed to download {} after {} attempts.".format(resource_url, MAX_ATTEMPTS))
        return False
