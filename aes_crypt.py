import pyAesCrypt
from os import stat, remove , urandom
import getpass
import argparse


def set_mode(**values):
    if values['crypt'] :
        mode = "encrypt"
    else :
        mode = "decrypt"
    return mode

class aes():
    def __init__(self,file,buffer, mode):
        self.file = file
        self.mode = mode
        if buffer not in range(8,256,8) :
            buffer = 64 * 1024
        else : buffer *= 1024
        self.buffer = buffer
    def getpassword(self):
        if self.mode =="decrypt" :
            self.password = getpass.getpass("Digit your decryption password : \n")
        else :
            first_input = getpass.getpass("Digit your encryption password : \n")
            second_input = getpass.getpass("Digit it again for double check : \n")
            while first_input != second_input :
                first_input = getpass.getpass("Wrong match ,digit your encryption password again : \n")
                second_input = getpass.getpass("Digit it again for double check : \n")
            self.password = first_input

    def action(self):
        if self.mode =="decrypt" : self.decrypt()
        else : self.encrypt()


    def secure_delete(self):
        with open(self.file, "ba+") as delfile:
            length = delfile.tell()
            for i in range(10):
                delfile.seek(0)
                delfile.write(urandom(length))
        remove(self.file)
    def encrypt(self):
        with open(self.file , "rb") as file_ingress:
            with open(self.file + ".aes", "wb") as encrypted_file:
                pyAesCrypt.encryptStream(file_ingress, encrypted_file, self.password, self.buffer)
        self.secure_delete()

    def decrypt(self):
        aes_file = self.file
        encFileSize = stat(aes_file).st_size
        if aes_file.endswith(".aes") :
            with open(aes_file, "rb") as file_ingress_aes :
                try:
                    file_output = aes_file.replace(".aes","")
                    with open(file_output, "wb") as file_decrypted :
                        # decrypt file stream
                        pyAesCrypt.decryptStream(file_ingress_aes, file_decrypted, self.password, self.buffer, encFileSize)
                except ValueError:
                    # remove output file on error
                    remove(file_output)
        else : raise ValueError("Value error file has not aes extention")

def main():
    my_parser = argparse.ArgumentParser(prog='aes_crypt',
                                        description='Pappaceglio \'s program for enc/decrypting files with AES256',
                                        usage='%(prog)s [options] path/file',
                                        epilog='Enjoy the program! :)')
    my_parser.add_argument('filename', action='store', metavar='filename', type=str,
                           help='the file to be encrypted or decrypted')
    # my_parser.add_argument('-c', '--crypt', action='store_true', help='set mode to encrypt the file')
    my_parser.add_argument('-b', '--buffer', action='store',type = int, help='set buffer to buffer_size*K enter a multiple of 8 in range 8-256')
    parser_group = my_parser.add_mutually_exclusive_group()
    parser_group.add_argument('-c', '--crypt', action='store_true', help='set mode to encrypt the file')
    parser_group.add_argument('-d', '--decrypt', action='store_true', help='set mode to decrypt the file')
    args = my_parser.parse_args()
    values = vars(args)
    file = values["filename"]
    buffer = values["buffer"]
    mode = set_mode(**values)
    AES = aes(file,buffer,mode)
    AES.getpassword()
    AES.action()

if __name__ == "__main__" : main()