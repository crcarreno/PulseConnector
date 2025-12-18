import subprocess
from pathlib import Path
from cryptography import x509
from datetime import datetime
from pathlib import Path

CERT_DIR = Path("certs")

def renew():
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", CERT_DIR / "key.pem",
        "-out", CERT_DIR / "cert.pem",
        "-days", "365",
        "-nodes",
        "-subj", "/CN=localhost"
    ], check=True)

if __name__ == "__main__":
    renew()


def cert_expires_soon(cert_path, days=30):
    cert = x509.load_pem_x509_certificate(
        Path(cert_path).read_bytes()
    )
    return (cert.not_valid_after - datetime.utcnow()).days < days
