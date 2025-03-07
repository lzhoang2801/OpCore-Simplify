from Scripts import run
from Scripts import utils
import platform
import json

os_name = platform.system()

class WifiProfileExtractor:
    def __init__(self):
        self.run = run.Run().run
        self.utils = utils.Utils()

    def validate_wifi_password(self, password):
        if not password:
            return False
        
        try:
            password.encode('ascii')
        except UnicodeEncodeError:
            return False
        
        if 8 <= len(password) <= 63 and all(32 <= ord(c) <= 126 for c in password):
            return True
            
        return False

    def get_wifi_password_macos(self, ssid):
        output = self.run({
            "args": ["security", "find-generic-password", "-wa", ssid]
        })

        if output[-1] != 0:
            return None
                
        try:
            ssid_info = json.loads(output[0].strip())
            password = ssid_info.get("password")
        except:
            password = output[0].strip() if output[0].strip() else None
            
        if password and self.validate_wifi_password(password):
            return password
        
        return None
        
    def get_wifi_password_windows(self, ssid):
        output = self.run({
            "args": ["netsh", "wlan", "show", "profile", ssid, "key=clear"]
        })

        if output[-1] != 0:
            return None

        for line in output[0].splitlines():
            if "Key Content" in line:
                password = line.split(":")[1].strip()
                if self.validate_wifi_password(password):
                    return password
        
        return None

    def get_wifi_password_linux(self, ssid):
        output = self.run({
            "args": ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", ssid]
        })

        if output[-1] != 0:
            return None

        password = output[0].strip()
        if self.validate_wifi_password(password):
            return password

        return None

    def ask_network_count(self, total_networks):
        self.utils.head("WiFi Network Retrieval")
        print("")
        print("Found {} WiFi networks on this device.".format(total_networks))
        print("")
        print("How many networks would you like to process?")
        print("  1-5 - Specific number (default: 5)")
        print("  A   - All available networks")
        print("")
        
        num_choice = self.utils.request_input("Enter your choice: ").strip().lower() or "5"
        
        if num_choice == "a":
            print("Will process all available networks.")
            return total_networks
        else:
            try:
                max_networks = min(int(num_choice), total_networks)
                print("Will process up to {} networks.".format(max_networks))
                return max_networks
            except:
                max_networks = min(5, total_networks)
                print("Invalid choice. Will process up to {} networks.".format(max_networks))
                return max_networks
            
    def process_networks(self, ssid_list, max_networks, get_password_func):
        networks = []
        processed_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while len(networks) < max_networks and processed_count < len(ssid_list):
            ssid = ssid_list[processed_count]
            
            try:
                print("")
                print("Processing {}/{}: {}".format(processed_count + 1, len(ssid_list), ssid))
                if os_name == "Darwin":
                    print("Please enter your administrator name and password or click 'Deny' to skip this network...")
                
                password = get_password_func(ssid)
                if password:
                    if (ssid, password) not in networks:
                        consecutive_failures = 0
                        networks.append((ssid, password))
                        print("Successfully retrieved password for {}".format(ssid))
                        
                        if len(networks) == max_networks:
                            break
                else:
                    consecutive_failures += 1 if os_name == "Darwin" else 0
                    print("Skipped or could not retrieve password for {}".format(ssid))

                    if consecutive_failures >= max_consecutive_failures:
                        continue_input = self.utils.request_input("\nUnable to retrieve passwords. Continue trying? (Y/n): ").strip().lower() or "y"
                        
                        if continue_input != "y":
                            break

                        consecutive_failures = 0
            except Exception as e:
                consecutive_failures += 1 if os_name == "Darwin" else 0
                print("Error processing network '{}': {}".format(ssid, str(e)))

                if consecutive_failures >= max_consecutive_failures:
                    continue_input = self.utils.request_input("\nUnable to retrieve passwords. Continue trying? (Y/n): ").strip().lower() or "y"

                    if continue_input != "y":
                        break

                    consecutive_failures = 0
            finally:
                processed_count += 1
            
            if processed_count >= max_networks and len(networks) < max_networks and processed_count < len(ssid_list):
                continue_input = self.utils.request_input("\nOnly retrieved {}/{} networks. Try more to reach your target? (Y/n): ".format(len(networks), max_networks)).strip().lower() or "y"
                
                if continue_input != "y":
                    break

                consecutive_failures = 0
        
        return networks

    def get_preferred_networks_macos(self, interface):
        output = self.run({
            "args": ["networksetup", "-listpreferredwirelessnetworks", interface]
        })

        if output[-1] != 0 or "Preferred networks on" not in output[0]:
            return []
        
        ssid_list = [network.strip() for network in output[0].splitlines()[1:] if network.strip()]
        
        if not ssid_list:
            return []
            
        max_networks = self.ask_network_count(len(ssid_list))
        
        self.utils.head("Administrator Authentication Required")
        print("")
        print("To retrieve WiFi passwords from the Keychain, macOS will prompt")
        print("you for administrator credentials for each WiFi network.")
        
        return self.process_networks(ssid_list, max_networks, self.get_wifi_password_macos)

    def get_preferred_networks_windows(self):
        output = self.run({
            "args": ["netsh", "wlan", "show", "profiles"]
        })

        if output[-1] != 0:
            return []
        
        ssid_list = []

        for line in output[0].splitlines():
            if "All User Profile" in line:
                try:
                    ssid = line.split(":")[1].strip()
                    if ssid:
                        ssid_list.append(ssid)
                except:
                    continue
        
        if not ssid_list:
            return []
            
        max_networks = self.ask_network_count(len(ssid_list))
    
        self.utils.head("WiFi Profile Extractor")
        print("")
        print("Ready to retrieve passwords for networks.")
        
        return self.process_networks(ssid_list, max_networks, self.get_wifi_password_windows)

    def get_preferred_networks_linux(self):
        output = self.run({
            "args": ["nmcli", "-t", "-f", "NAME", "connection", "show"]
        })

        if output[-1] != 0:
            return []
        
        ssid_list = [network.strip() for network in output[0].splitlines() if network.strip()]
        
        if not ssid_list:
            return []
            
        max_networks = self.ask_network_count(len(ssid_list))
    
        self.utils.head("WiFi Profile Extractor")
        print("")
        print("Ready to retrieve passwords for networks.")
        
        return self.process_networks(ssid_list, max_networks, self.get_wifi_password_linux)

    def get_wifi_interfaces(self):
        output = self.run({
            "args": ["networksetup", "-listallhardwareports"]
        })

        if output[-1] != 0:
            return []
        
        interfaces = []
        
        for interface_info in output[0].split("\n\n"):
            if "Device: en" in interface_info:
                try:
                    interface = "en{}".format(int(interface_info.split("Device: en")[1].split("\n")[0]))
                    
                    test_output = self.run({
                        "args": ["networksetup", "-listpreferredwirelessnetworks", interface]
                    })

                    if test_output[-1] == 0 and "Preferred networks on" in test_output[0]:
                        interfaces.append(interface)
                except:
                    continue

        return interfaces
    
    def get_profiles(self):
        os_name = platform.system()

        self.utils.head("WiFi Profile Extractor")
        print("")
        print("\033[93mNote:\033[0m")
        print("- When using itlwm kext, WiFi appears as Ethernet in macOS")
        print("- You'll need Heliport app to manage WiFi connections in macOS")
        print("- This step will enable auto WiFi connections at boot time")
        print("  and is useful for users installing macOS via Recovery OS")
        print("")
        
        user_input = self.utils.request_input("Would you like to scan for WiFi profiles? (Y/n): ").strip().lower() or "y"
        if user_input != "y":
            return []

        profiles = []
        self.utils.head("Detecting WiFi Profiles")
        print("")
        print("Scanning for WiFi profiles...")
        
        if os_name == "Windows":
            profiles = self.get_preferred_networks_windows()
        elif os_name == "Darwin":
            wifi_interfaces = self.get_wifi_interfaces()

            if wifi_interfaces:
                for interface in wifi_interfaces:
                    print("Checking interface: {}".format(interface))
                    interface_profiles = self.get_preferred_networks_macos(interface)
                    if interface_profiles:
                        profiles = interface_profiles
                        break
            else:
                print("No WiFi interfaces detected.")
        elif os_name == "Linux":
            profiles = self.get_preferred_networks_linux()

        if not profiles:
            self.utils.head("WiFi Profile Extractor")
            print("")
            print("No WiFi profiles with saved passwords were found.")
            self.utils.request_input()
        
        self.utils.head("WiFi Profile Extractor")
        print("")
        print("Found the following WiFi profiles with saved passwords:")
        print("")
        print("Index  SSID                    Password")
        print("-------------------------------------------------------")
        for index, (ssid, password) in enumerate(profiles, start=1):
            print("{:<6} {:<23} {}".format(index, ssid[:23], password))
        print("")
        print("Successfully applied {} WiFi profiles.".format(len(profiles)))
        print("")
            
        self.utils.request_input()
        return profiles
