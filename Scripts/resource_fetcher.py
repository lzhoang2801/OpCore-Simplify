from Scripts import integrity_checker
from Scripts import utils
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

MAX_ATTEMPTS = 3

class ResourceFetcher:
    def __init__(self, utils_instance=None, integrity_checker_instance=None, headers=None):
        self.request_headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.utils = utils_instance if utils_instance else utils.Utils()
        self.buffer_size = 16 * 1024
        self.ssl_context = self.create_ssl_context()
        self.integrity_checker = integrity_checker_instance if integrity_checker_instance else integrity_checker.IntegrityChecker()

    def create_ssl_context(self):
        try:
            cafile = ssl.get_default_verify_paths().openssl_cafile
            if not os.path.exists(cafile):
                import certifi
                cafile = certifi.where()
            ssl_context = ssl.create_default_context(cafile=cafile)
            self.utils.log_message("[RESOURCE FETCHER] Created SSL context", level="INFO")
        except Exception as e:
            ssl_context = ssl._create_unverified_context()
            self.utils.log_message("[RESOURCE FETCHER] Created unverified SSL context", level="INFO")
        return ssl_context

    def _make_request(self, resource_url, timeout=10):
        try:
            headers = dict(self.request_headers)
            headers["Accept-Encoding"] = "gzip, deflate"
            
            return urlopen(Request(resource_url, headers=headers), timeout=timeout, context=self.ssl_context)
        except socket.timeout as e:
            self.utils.log_message("[RESOURCE FETCHER] Timeout error: {}".format(e), level="ERROR", to_build_log=True)
        except ssl.SSLError as e:
            self.utils.log_message("[RESOURCE FETCHER] SSL error: {}".format(e), level="ERROR", to_build_log=True)
        except (URLError, socket.gaierror) as e:
            self.utils.log_message("[RESOURCE FETCHER] Connection error: {}".format(e), level="ERROR", to_build_log=True)
        except Exception as e:
            self.utils.log_message("[RESOURCE FETCHER] Request failed: {}".format(e), level="ERROR", to_build_log=True)

        return None

    def fetch_and_parse_content(self, resource_url, content_type=None):
        attempt = 0
        response = None

        self.utils.log_message("[RESOURCE FETCHER] Fetching and parsing content from {}".format(resource_url), level="INFO")

        while attempt < MAX_ATTEMPTS:
            response = self._make_request(resource_url)

            if not response:
                attempt += 1
                self.utils.log_message("[RESOURCE FETCHER] Failed to fetch content from {}. Retrying...".format(resource_url), level="WARNING", to_build_log=True)
                continue

            if response.getcode() == 200:
                break

            attempt += 1

        if not response:
            self.utils.log_message("[RESOURCE FETCHER] Failed to fetch content from {}".format(resource_url), level="ERROR", to_build_log=True)
            return None
        
        content = response.read()

        if response.info().get("Content-Encoding") == "gzip" or content.startswith(b"\x1f\x8b"):
            try:
                content = gzip.decompress(content)
            except Exception as e:
                self.utils.log_message("[RESOURCE FETCHER] Failed to decompress gzip content: {}".format(e), level="ERROR", to_build_log=True)
        elif response.info().get("Content-Encoding") == "deflate":
            try:
                content = zlib.decompress(content)
            except Exception as e:
                self.utils.log_message("[RESOURCE FETCHER] Failed to decompress deflate content: {}".format(e), level="ERROR", to_build_log=True)
        
        try:
            if content_type == "json":
                return json.loads(content)
            elif content_type == "plist":
                return plistlib.loads(content)
            else:
                return content.decode("utf-8")
        except Exception as e:
            self.utils.log_message("[RESOURCE FETCHER] Error parsing content as {}: {}".format(content_type, e), level="ERROR", to_build_log=True)
            
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
            
            self.utils.log_message("[RESOURCE FETCHER] Download progress: {}".format(progress), level="INFO", to_build_log=True)

    def download_and_save_file(self, resource_url, destination_path, sha256_hash=None):
        attempt = 0

        self.utils.log_message("[RESOURCE FETCHER] Downloading and saving file from {} to {}".format(resource_url, destination_path), level="INFO")

        while attempt < MAX_ATTEMPTS:
            attempt += 1
            response = self._make_request(resource_url)

            if not response:
                self.utils.log_message("[RESOURCE FETCHER] Failed to fetch content from {}. Retrying...".format(resource_url), level="WARNING", to_build_log=True)
                continue

            with open(destination_path, "wb") as local_file:
                self._download_with_progress(response, local_file)

            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                if sha256_hash:
                    self.utils.log_message("[RESOURCE FETCHER] Verifying SHA256 checksum...", level="INFO", to_build_log=True)
                    downloaded_hash = self.integrity_checker.get_sha256(destination_path)
                    if downloaded_hash.lower() == sha256_hash.lower():
                        self.utils.log_message("[RESOURCE FETCHER] Checksum verified successfully.", level="INFO", to_build_log=True)
                        return True
                    else:
                        self.utils.log_message("[RESOURCE FETCHER] Checksum mismatch! Removing file and retrying download...", level="WARNING", to_build_log=True)
                        os.remove(destination_path)
                        continue
                else:
                    self.utils.log_message("[RESOURCE FETCHER] No SHA256 hash provided. Downloading file without verification.", level="INFO", to_build_log=True)
                    return True
            
            if os.path.exists(destination_path):
                os.remove(destination_path)

            if attempt < MAX_ATTEMPTS:
                self.utils.log_message("[RESOURCE FETCHER] Download failed for {}. Retrying...".format(resource_url), level="WARNING", to_build_log=True)

        self.utils.log_message("[RESOURCE FETCHER] Failed to download {} after {} attempts.".format(resource_url, MAX_ATTEMPTS), level="ERROR", to_build_log=True)
        return False