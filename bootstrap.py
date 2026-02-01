from pathlib import Path
from analytics.logger import setup_logger
from database.db_config import config_db
from security.password_hasher import PasswordHasher
from security.iam_services import IAMService
from security.config_services import load_config
from security.certs.admin_certs import generate_ca, generate_server_cert, save_pem

iam = IAMService(config_db)
log = setup_logger()

APP_NAME = "PulseConnector"


def run_bootstrap():
    """
    Bootstrap process:
    - Ensure certificates exist
    - Ensure default admin user exists
    """
    cfg = load_config()

    ensure_certificates(cfg)
    ensure_admin_user()

    log.info("Bootstrap completed successfully")


def ensure_certificates(cfg):

    sec = cfg.get("security", {})

    base_path = Path.home() / ".config" / APP_NAME / "certs"
    base_path.mkdir(parents=True, exist_ok=True)

    cert_path = base_path / "cert.pem"
    key_path = base_path / "key.pem"

    if cert_path.exists() and key_path.exists():
        log.info("Certificates already exist")
    else:
        log.warning("Certificates not found, generating new ones")

        ca_key, ca_cert = generate_ca()
        server_key, server_cert = generate_server_cert(
            ca_key, ca_cert, hostname="localhost"
        )

        save_pem(base_path, server_key, server_cert)
        log.info("Certificates generated successfully")

    sec["cert"] = str(cert_path)
    sec["key"] = str(key_path)


def ensure_admin_user():

    try:
        iam.get_user("admin")
        log.info("Admin user already exists")
        return
    except ValueError:
        pass  # user does not exist → create it

    hasher = PasswordHasher()
    password_hash = hasher.hash_password("admin123")

    iam.create_user(
        user="admin",
        display="Administrator",
        password=password_hash
    )

    log.warning("Admin user created with temporary password: admin123")

