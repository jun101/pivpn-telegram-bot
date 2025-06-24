import os
from io import BytesIO

class PiVPNManager:
    def __init__(self, config_dir="./mock_configs"):
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
    
    def add_profile(self, profile_name: str) -> str:
        # Create a fake config file with basic content
        conf_path = os.path.join(self.config_dir, f"{profile_name}.conf")
        with open(conf_path, "w") as f:
            f.write(f"[Interface]\nPrivateKey = MOCK_PRIVATE_KEY\nAddress = 10.0.0.2/24\n\n[Peer]\nPublicKey = MOCK_PUBLIC_KEY\nAllowedIPs = 0.0.0.0/0\n")
        return conf_path

    def list_profiles(self):
        profiles = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".conf"):
                profiles.append(filename[:-5])  # Remove '.conf'
        return profiles

    def revoke_profile(self, profile_name: str) -> bool:
        conf_path = os.path.join(self.config_dir, f"{profile_name}.conf")
        if os.path.isfile(conf_path):
            os.remove(conf_path)
            return True
        return False
