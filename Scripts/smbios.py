from Scripts import gathering_files
from Scripts import utils
import os
import subprocess
import uuid
import random

class SMBIOS:
    def __init__(self):
        self.g = gathering_files.gatheringFiles()
        self.utils = utils.Utils()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.macserial = self.check_macserial()

    def check_macserial(self, quit=False):
        macserial_name = "macserial.exe" if os.name == "nt" else "macserial"
        macserial_path = os.path.join(self.script_dir, macserial_name)

        if not os.path.exists(macserial_path):
            download_history = self.utils.read_file(self.g.download_history_file)

            if download_history:
                product_index = self.g.product_index_in_history("OpenCore", download_history["versions"])
                
                if product_index:
                    download_history["versions"].pop(product_index)
                    download_history["last_updated"] = "2024-07-25T12:00:00"
                    self.utils.write_file(self.g.download_history_file, download_history)

            if quit:
                raise Exception("{} not found. Please reopen the program to download it".format(macserial_name))
        else:
            return macserial_path

    def generate_random_mac(self):
        random_mac = ''.join([format(random.randint(0, 255), '02X') for _ in range(6)])
        return random_mac

    def generate(self, product_name):
        if not self.macserial:
            self.check_macserial(True)

        random_mac_address = self.generate_random_mac()

        result = subprocess.run(
            [self.macserial, "-g", "--model", product_name],
            capture_output=True,
            check=True,  # Raises CalledProcessError for non-zero return code
        )
        first_serial = result.stdout.decode().splitlines()[0]

        return {
            "MLB": "A" + "0"*15 + "Z" if not " | " in first_serial else first_serial.split(" | ")[-1],
            "ROM": random_mac_address,
            "SystemProductName": product_name,
            "SystemSerialNumber": "A" + "0"*10 + "9" if not " | " in first_serial else first_serial.split(" | ")[0],
            "SystemUUID": str(uuid.uuid4()).upper(),
        }