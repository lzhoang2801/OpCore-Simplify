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
RETRY_DELAY_SECONDS = 2
STALL_TIMEOUT_SECONDS = 60

class ResourceFetcher:
    def __init__(self, headers=None, utils_instance=None):
        self.request_headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.buffer_size = 16 * 1024
        self.ssl_context = self.create_ssl_context()
        self.integrity_checker = integrity_checker.IntegrityChecker()
        self.utils = utils_instance if utils_instance is not None else utils.Utils()

    def create_ssl_context(self):
        try:
            cafile = ssl.get_default_verify_paths().openssl_cafile
            if not os.path.exists(cafile):
                import certifi
                cafile = certifi.where()
            ssl_context = ssl.create_default_context(cafile=cafile)
        except Exception as e:
            print(f"Failed to create SSL context: {e}")
            ssl_context = ssl._create_unverified_context()
        return ssl_context

    def _make_request(self, resource_url, timeout=30):
        try:
            headers = dict(self.request_headers)
            headers["Accept-Encoding"] = "gzip, deflate"
            
            return urlopen(Request(resource_url, headers=headers), timeout=timeout, context=self.ssl_context)
        except socket.timeout as e:
            print(f"Timeout error: {e}")
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
        except (URLError, socket.gaierror) as e:
            print(f"Connection error: {e}")
        except Exception as e:
            print(f"Request failed: {e}")

        return None

    def fetch_and_parse_content(self, resource_url, content_type=None):
        attempt = 0
        response = None

        while attempt < 3:
            # Close previous response from failed attempt before retrying
            if response:
                response.close()
                response = None
            
            response = self._make_request(resource_url)

            if not response:
                attempt += 1
                print(f"Failed to fetch content from {resource_url}. Retrying...")
                continue

            if response.getcode() == 200:
                break

            attempt += 1

        if not response:
            print(f"Failed to fetch content from {resource_url}")
            return None
        
        try:
            content = response.read()

            if response.info().get("Content-Encoding") == "gzip" or content.startswith(b"\x1f\x8b"):
                try:
                    content = gzip.decompress(content)
                except Exception as e:
                    print(f"Failed to decompress gzip content: {e}")
            elif response.info().get("Content-Encoding") == "deflate":
                try:
                    content = zlib.decompress(content)
                except Exception as e:
                    print(f"Failed to decompress deflate content: {e}")
            
            try:
                if content_type == "json":
                    return json.loads(content)
                elif content_type == "plist":
                    return plistlib.loads(content)
                else:
                    return content.decode("utf-8")
            except Exception as e:
                print(f"Error parsing content as {content_type}: {e}")
                
            return None
        finally:
            # Always close the response to prevent resource leaks
            if response:
                response.close()

    def _download_with_progress(self, response, local_file):
        total_size = response.getheader("Content-Length")
        if total_size:
            total_size = int(total_size)
        bytes_downloaded = 0
        start_time = time.time()
        last_time = start_time
        last_bytes = 0
        speeds = []
        
        # Stall detection variables
        stall_timeout = STALL_TIMEOUT_SECONDS
        last_progress_time = time.time()
        last_progress_bytes = 0

        speed_str = "-- KB/s"
        
        # Check if we're in GUI mode (utils has gui_callback set)
        is_gui_mode = self.utils.gui_callback is not None
        
        # GUI mode progress tracking - to avoid flooding console with too many updates
        last_progress = ""  # Last progress string printed (GUI mode)
        last_mb_printed = -1  # Last megabyte boundary printed (GUI mode)
        
        while True:
            try:
                chunk = response.read(self.buffer_size)
            except socket.timeout:
                print("\nDownload stalled - connection timeout while reading data")
                raise Exception("Download stalled - connection timeout")
            except Exception as e:
                print(f"\nError reading data: {e}")
                raise
                
            if not chunk:
                break
            local_file.write(chunk)
            bytes_downloaded += len(chunk)
            
            current_time = time.time()
            time_diff = current_time - last_time
            
            # Check for stall - no progress for stall_timeout seconds
            if bytes_downloaded > last_progress_bytes:
                last_progress_time = current_time
                last_progress_bytes = bytes_downloaded
            elif current_time - last_progress_time > stall_timeout:
                print(f"\nDownload appears to be stalled (no progress for {stall_timeout} seconds)")
                raise Exception(f"Download stalled - no progress for {stall_timeout} seconds")
            
            if time_diff > 0.5:
                current_speed = (bytes_downloaded - last_bytes) / time_diff
                speeds.append(current_speed)
                if len(speeds) > 5:
                    speeds.pop(0)
                avg_speed = sum(speeds) / len(speeds)
                
                if avg_speed < 1024*1024:
                    speed_str = f"{avg_speed/1024:.1f} KB/s"
                else:
                    speed_str = f"{avg_speed/(1024*1024):.1f} MB/s"
                
                last_time = current_time
                last_bytes = bytes_downloaded
            
            if total_size:
                percent = int(bytes_downloaded / total_size * 100)
                bar_length = 40
                filled = int(bar_length * bytes_downloaded / total_size)
                bar = "█" * filled + "░" * (bar_length - filled)
                progress = f"{speed_str} [{bar}] {percent:3d}% {bytes_downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f}MB"
            else:
                progress = f"{speed_str} {bytes_downloaded/(1024*1024):.1f}MB downloaded"
            
            # In GUI mode, print on new lines; in CLI mode, use carriage return
            if is_gui_mode:
                # Only print every 1MB to avoid flooding the GUI console
                current_mb = bytes_downloaded // (1024*1024)
                mb_boundary_crossed = current_mb > last_mb_printed
                
                # Print progress every MB to give user feedback without flooding
                if mb_boundary_crossed:
                    print(progress)
                    last_progress = progress
                    last_mb_printed = current_mb
            else:
                # CLI mode: use carriage return for in-place updates
                print(" " * 80, end="\r")
                print(progress, end="\r")
            
        # Final newline
        if not is_gui_mode:
            print()

    def download_and_save_file(self, resource_url, destination_path, sha256_hash=None):
        attempt = 0

        while attempt < MAX_ATTEMPTS:
            attempt += 1
            response = self._make_request(resource_url)

            if not response:
                print(f"Failed to fetch content from {resource_url}. Retrying...")
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            try:
                with open(destination_path, "wb") as local_file:
                    self._download_with_progress(response, local_file)
            except Exception as e:
                print(f"Error during download: {e}")
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                if attempt < MAX_ATTEMPTS:
                    print(f"Retrying download (attempt {attempt + 1}/{MAX_ATTEMPTS})...")
                    time.sleep(RETRY_DELAY_SECONDS)
                    continue
                else:
                    # Final attempt failed, return False to indicate failure
                    return False
            finally:
                # Always close the response to prevent resource leaks
                # The response is only needed during download; verification reads from the local file
                if response:
                    response.close()

            if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                if sha256_hash:
                    print("Verifying SHA256 checksum...")
                    downloaded_hash = self.integrity_checker.get_sha256(destination_path)
                    if downloaded_hash.lower() == sha256_hash.lower():
                        print("Checksum verified successfully.")
                        return True
                    else:
                        print("Checksum mismatch! Removing file and retrying download...")
                        os.remove(destination_path)
                        time.sleep(RETRY_DELAY_SECONDS)
                        continue
                else:
                    print("No SHA256 hash provided. Downloading file without verification.")
                    return True
            
            if os.path.exists(destination_path):
                os.remove(destination_path)

            if attempt < MAX_ATTEMPTS:
                print(f"Download failed for {resource_url}. Retrying...")
                time.sleep(RETRY_DELAY_SECONDS)

        print(f"Failed to download {resource_url} after {MAX_ATTEMPTS} attempts.")
        return False