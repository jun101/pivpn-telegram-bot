import os
from bot.utils.logger import logger

class PiVPNManager:
    def __init__(self, config_dir="./mock_configs"):
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        logger.info(f"Mock PiVPNManager initialized with config dir: {self.config_dir}")

    def add_profile(self, profile_name: str) -> str:
        conf_path = os.path.join(self.config_dir, f"{profile_name}.conf")
        with open(conf_path, "w") as f:
            f.write(
                "[Interface]\n"
                "PrivateKey = MOCK_PRIVATE_KEY\n"
                "Address = 10.0.0.2/24\n\n"
                "[Peer]\n"
                "PublicKey = MOCK_PUBLIC_KEY\n"
                "AllowedIPs = 0.0.0.0/0\n"
            )
        logger.info(f"Mock profile '{profile_name}' created at {conf_path}")
        return conf_path

    def list_profiles(self):
        profiles = [
            filename[:-5]  # Remove '.conf'
            for filename in os.listdir(self.config_dir)
            if filename.endswith(".conf")
        ]
        logger.info(f"Listing profiles: {profiles}")
        return profiles

    def get_profile_qr(self, profile_name: str):
        # Return mock QR code data as bytes
        logger.info(f"Generating mock QR code for profile '{profile_name}'")
        return f"MOCK_QR_CODE_DATA_FOR_{profile_name}".encode()

    def revoke_profile(self, profile_name: str) -> bool:
        conf_path = os.path.join(self.config_dir, f"{profile_name}.conf")
        if os.path.isfile(conf_path):
            os.remove(conf_path)
            logger.info(f"Mock profile '{profile_name}' revoked (deleted).")
            return True
        logger.warning(f"Mock profile '{profile_name}' not found to revoke.")
        return False
