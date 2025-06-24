import os
import subprocess
from bot.utils.logger import logger  # your logger setup

class PiVPNManager:
    def __init__(self):
        self.config_dir = os.getenv("PIVPN_CONFIG_DIR", "/etc/wireguard")
        logger.info(f"PiVPNManager initialized with config_dir: {self.config_dir}")

    def add_profile(self, profile_name: str) -> str:
        cmd = ["pivpn", "-a", "-n", profile_name, "-q"]
        logger.info(f"Adding VPN profile '{profile_name}' with command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            conf_path = os.path.join(self.config_dir, f"{profile_name}.conf")
            if os.path.isfile(conf_path):
                logger.info(f"Profile '{profile_name}' created at: {conf_path}")
                return conf_path
            else:
                logger.error(f"Config file for '{profile_name}' not found after creation.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add profile '{profile_name}': {e}")
        return ""

    def list_profiles(self):
        profiles = []
        try:
            for filename in os.listdir(self.config_dir):
                if filename.endswith(".conf"):
                    profiles.append(filename[:-5])
            logger.info(f"Found profiles: {profiles}")
        except FileNotFoundError:
            logger.error(f"Config directory '{self.config_dir}' does not exist.")
        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
        return profiles

    def revoke_profile(self, profile_name: str) -> bool:
        cmd = ["pivpn", "-r", "-n", profile_name, "-q"]
        logger.info(f"Revoking VPN profile '{profile_name}' with command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Profile '{profile_name}' revoked successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to revoke profile '{profile_name}': {e}")
        return False
