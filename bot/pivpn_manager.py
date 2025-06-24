import os
import subprocess
from bot.utils.logger import logger  # your logger setup

class PiVPNManager:
    def __init__(self):
        self.config_dir = os.getenv("PIVPN_CONFIG_DIR", "/etc/wireguard")
        logger.info(f"PiVPNManager initialized with config_dir: {self.config_dir}")

    def add_profile(self, profile_name: str) -> str:
        cmd = ["pivpn", "-a", "-n", profile_name]
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
        try:
            profiles = [
                filename[:-5]  # Remove '.conf'
                for filename in os.listdir(self.config_dir)
                if filename.endswith(".conf")
            ]
            logger.info(f"Found profiles: {profiles}")
            return profiles
        except FileNotFoundError:
            logger.error(f"Config directory '{self.config_dir}' does not exist.")
        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
        return []

    def get_profile_qr(self, profile_name: str):
        try:
            config_path = os.path.join(self.config_dir, f"{profile_name}.conf")
            if not os.path.isfile(config_path):
                logger.warning(f"Config file not found for profile '{profile_name}'")
                return None

            # Generate QR code PNG bytes using qrencode
            result = subprocess.run(
                ["qrencode", "-t", "PNG", "-o", "-", "-r", config_path],
                capture_output=True,
                check=True,
            )
            logger.info(f"Generated QR code for profile '{profile_name}'")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate QR code for profile '{profile_name}': {e}")
        except Exception as e:
            logger.error(f"Error generating QR code for profile '{profile_name}': {e}")
        return None

    def revoke_profile(self, profile_name: str) -> bool:
        cmd = ["pivpn", "-r", "-n", profile_name]
        logger.info(f"Revoking VPN profile '{profile_name}' with: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, input="y\n", text=True, check=True)
            logger.info(f"Profile '{profile_name}' revoked successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to revoke profile '{profile_name}': {e}")
            return False


