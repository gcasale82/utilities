import ftplib
import ssl
import socket

class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass that automatically wraps sockets in SSL to support implicit FTPS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sock = None

    @property
    def sock(self):
        """Return the socket."""
        return self._sock

    @sock.setter
    def sock(self, value):
        """When modifying the socket, ensure that it is ssl wrapped."""
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)
        self._sock = value

host = "test.rebex.net"
user = "demo"
password = "password"
port = 990

ftp_client = ImplicitFTP_TLS()
ftp_client.connect(host, port)
ftp_client.login(user, password)
ftp_client.prot_p()
print(ftp_client.nlst())
ftp_client.close()