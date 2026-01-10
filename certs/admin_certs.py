from ipaddress import ip_address

from cryptography import x509
from cryptography.hazmat._oid import ExtendedKeyUsageOID
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from analytics.logger import setup_logger

log = setup_logger()


def generate_ca():

    try:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "EC"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PulseConnector Local CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "PulseConnector CA"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(key, hashes.SHA256())
        )

        return key, cert
    except Exception as e:
        log.error("Error: {}".format(e))
        raise e

'''
def generate_server_cert(ca_key, ca_cert, hostname="localhost"):
    try:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=825))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(hostname),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            )
            .sign(ca_key, hashes.SHA256())
        )

        return key, cert

    except Exception as e:
        log.error("Error: {}".format(e))
        raise e
'''

def generate_server_cert(ca_key, ca_cert, hostname="localhost"):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ]))
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=825))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("localhost.localdomain"),
                x509.IPAddress(ip_address("127.0.0.1")),
                x509.IPAddress(ip_address("::1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH
            ]),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return key, cert

def save_pem(path, key, cert):

    try:
        with open(path / "key.pem", "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(path / "cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    except Exception as e:
        log.error("Error: {}".format(e))
        raise e