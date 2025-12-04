from Scripts import run
from Scripts import utils
import platform
import json

os_name = platform.system()

class WifiProfileExtractor:
    def __init__(self, utils_instance=None):
        self.run = run.Run().run
        self.utils = utils_instance if utils_instance is not None else utils.Utils()

    def get_authentication_type(self, authentication_type):
        authentication_type = authentication_type.lower()

        open_types = ("none", "owe", "open")
        for open_type in open_types:
            if open_type in authentication_type:
                return "open"

        if "wep" in authentication_type or "shared" in authentication_type:
            return "wep"
        
        if "wpa" in authentication_type or "sae" in authentication_type:
            return "wpa"
        
        return None

    def validate_wifi_password(self, authentication_type=None, password=None):
        print("Validating password with authentication type: {}".format(authentication_type))

        if password is None:
            return None

        if authentication_type is None:
            return password

        if authentication_type == "open":
            return ""

        try:
            password.encode('ascii')
        except UnicodeEncodeError:
            return None
            
        if 8 <= len(password) <= 63 and all(32 <= ord(c) <= 126 for c in password):
            return password
                
        return None

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
            
        return self.validate_wifi_password("wpa", password)
        
    def get_wifi_password_windows(self, ssid):
        output = self.run({
            "args": ["netsh", "wlan", "show", "profile", ssid, "key=clear"]
        })

        if output[-1] != 0:
            return None

        authentication_type = None
        password = None

        for line in output[0].splitlines():
            if authentication_type is None and "Authentication" in line:
                authentication_type = self.get_authentication_type(line.split(":")[1].strip())
            elif "Key Content" in line:
                password = line.split(":")[1].strip()

        return self.validate_wifi_password(authentication_type, password)

    def get_wifi_password_linux(self, ssid):
        output = self.run({
            "args": ["nmcli", "--show-secrets", "connection", "show", ssid]
        })

        if output[-1] != 0:
            return None
        
        authentication_type = None
        password = None

        for line in output[0].splitlines():
            if "802-11-wireless-security.key-mgmt:" in line:
                authentication_type = self.get_authentication_type(line.split(":")[1].strip())
            elif "802-11-wireless-security.psk:" in line:
                password = line.split(":")[1].strip()

        return self.validate_wifi_password(authentication_type, password)

    def ask_network_count(self, total_networks):
        self.utils.head("WiFi Network Retrieval")
        print("")
        print("Found {} WiFi networks on this device.".format(total_networks))
        print("")
        print("How many networks would you like to process?")
        print("  1-{} - Specific number (default: 5)".format(total_networks))
        print("  A   - All available networks")
        print("")
        
        num_choice = self.utils.request_input("Enter your choice: ").strip().lower() or "5"
        
        if num_choice == "a":
            print("Will process all available networks.")
            return total_networks

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
                    print("Please enter your administrator name and password or click 'Deny' to skip this network.")
                
                password = get_password_func(ssid)
                if password is not None:
                    if (ssid, password) not in networks:
                        consecutive_failures = 0
                        networks.append((ssid, password))
                        print("Successfully retrieved password.")
                        
                        if len(networks) == max_networks:
                            break
                else:
                    consecutive_failures += 1 if os_name == "Darwin" else 0
                    print("Could not retrieve password for this network.")

                    if consecutive_failures >= max_consecutive_failures:
                        continue_input = self.utils.request_input("\nUnable to retrieve passwords. Continue trying? (Yes/no): ").strip().lower() or "yes"
                        
                        if continue_input != "yes":
                            break

                        consecutive_failures = 0
            except Exception as e:
                consecutive_failures += 1 if os_name == "Darwin" else 0
                print("Error processing network '{}': {}".format(ssid, str(e)))

                if consecutive_failures >= max_consecutive_failures:
                    continue_input = self.utils.request_input("\nUnable to retrieve passwords. Continue trying? (Yes/no): ").strip().lower() or "yes"

                    if continue_input != "yes":
                        break

                    consecutive_failures = 0
            finally:
                processed_count += 1
            
            if processed_count >= max_networks and len(networks) < max_networks and processed_count < len(ssid_list):
                continue_input = self.utils.request_input("\nOnly retrieved {}/{} networks. Try more to reach your target? (Yes/no): ".format(len(networks), max_networks)).strip().lower() or "yes"
                
                if continue_input != "yes":
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

        max_networks = len(ssid_list)
    
        self.utils.head("WiFi Profile Extractor")
        print("")
        print("Retrieving passwords for {} network(s)...".format(len(ssid_list)))
        
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
            
        max_networks = len(ssid_list)
    
        self.utils.head("WiFi Profile Extractor")
        print("")
        print("Retrieving passwords for {} network(s)...".format(len(ssid_list)))
        
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

        # Check if GUI mode - use dialog
        if self.utils.gui_callback:
            # Import here to avoid circular dependencies
            from Scripts.gui.custom_dialogs import show_wifi_profile_extractor_dialog
            
            # Get the parent window from utils if available
            parent = getattr(self.utils, 'gui_parent', None)
            
            # Show the WiFi profile extractor dialog
            user_wants_scan = show_wifi_profile_extractor_dialog(parent)
            
            if not user_wants_scan:
                return []
        else:
            # CLI mode - use original prompts
            self.utils.head("WiFi Profile Extractor")
            print("")
            print("\033[1;93mNote:\033[0m")
            print("- When using itlwm kext, WiFi appears as Ethernet in macOS")
            print("- You'll need Heliport app to manage WiFi connections in macOS")
            print("- This step will enable auto WiFi connections at boot time")
            print("  and is useful for users installing macOS via Recovery OS")
            print("")
            
            while True:
                user_input = self.utils.request_input("Would you like to scan for WiFi profiles? (Yes/no): ").strip().lower()
                
                if user_input == "yes":
                    break
                elif user_input == "no":
                    return []
                else:
                    print("\033[91mInvalid selection, please try again.\033[0m\n\n")

        profiles = []
        self.utils.head("Detecting WiFi Profiles")
        print("")
        print("Scanning for WiFi profiles...")
        
        if os_name == "Windows":
            profiles = self.get_preferred_networks_windows()
        elif os_name == "Linux":
            profiles = self.get_preferred_networks_linux()
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

        if not profiles:
            self.utils.head("WiFi Profile Extractor")
            print("")
            print("No WiFi profiles with saved passwords were found.")
            # Only show "Press Enter to continue" prompt in CLI mode
            if not self.utils.gui_callback:
                self.utils.request_input()
        else:
            self.utils.head("WiFi Profile Extractor")
            print("")
            print("Found the following WiFi profiles with saved passwords:")
            print("")
            print("Index  SSID                             Password")
            print("-------------------------------------------------------")
            for index, (ssid, password) in enumerate(profiles, start=1):
                print("{:<6} {:<32} {:<8}".format(index, ssid[:31] + "..." if len(ssid) > 31 else ssid, password[:12] + "..." if len(password) > 12 else password))
            print("")
            print("Successfully applied {} WiFi profiles.".format(len(profiles)))
            print("")
            
            # Only show "Press Enter to continue" prompt in CLI mode
            if not self.utils.gui_callback:
                self.utils.request_input()
        return profiles