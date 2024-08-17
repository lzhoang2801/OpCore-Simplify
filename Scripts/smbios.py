from Scripts import gathering_files
from Scripts import run
from Scripts import utils
import os
import subprocess
import uuid
import random

class SMBIOS:
    def __init__(self):
        self.g = gathering_files.gatheringFiles()
        self.run = run.Run().run
        self.utils = utils.Utils()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

    def check_macserial(self):
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

            raise Exception("{} not found. Please reopen the program to download it".format(macserial_name))
        
        return macserial_path

    def generate_random_mac(self):
        random_mac = ''.join([format(random.randint(0, 255), '02X') for _ in range(6)])
        return random_mac

    def generate(self, product_name):
        macserial = self.check_macserial()

        random_mac_address = self.generate_random_mac()

        output = self.run({
            "args":[macserial, "-g", "--model", product_name]
        })
        
        if output[-1] != 0 or not " | " in output[0]:
            serial = []
        else:
            serial = output[0].splitlines()[0].split(" | ")

        return {
            "MLB": "A" + "0"*15 + "Z" if not serial else serial[-1],
            "ROM": random_mac_address,
            "SystemProductName": product_name,
            "SystemSerialNumber": "A" + "0"*10 + "9" if not serial else serial[0],
            "SystemUUID": str(uuid.uuid4()).upper(),
        }