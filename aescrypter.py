from getpass import getpass
from Cryptodome.Random import get_random_bytes
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Cipher import AES
import os
import datetime
import shutil
import argparse
from sys import exit
from re import search

status = False
salt = get_random_bytes(32)  # Generate salt
BUFFER_SIZE = 64 * 1024
def get_out_filepath(filepath):
    if os.path.exists(filepath + '.aes') :
        suffix = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        out_filepath = filepath + suffix + '.aes'
        return out_filepath
    else :
        return filepath + '.aes'
        
def get_decrypted_filepath(filepath) :
    out_filepath = os.path.splitext(filepath)[0]
    if os.path.splitext(filepath)[1] == '.aes' :
        if os.path.exists(out_filepath) :
            suffix = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
            out_filepath += suffix
        return out_filepath
    else :
        print("wrong filetype , only aes files can be decrypted !")
        exit()

def encrypt_password():
    first_password = getpass("Insert your password : \n")
    if len(first_password) < 8 :
        print("Password is too short ! \n")
        return False
    if not search(r"[A-Z]" , first_password) :
        print("Password weak does not contain uppercase !")
        return False
    if not search(r"[a-z]" , first_password) :
        print(" Password weak does not contain lowercase !")
        return False
    if not search(r"[0-9]" , first_password) :
        print("Password weak does not contain number !")
        return False
    second_password = getpass(" Type your password again : \n")
    if first_password == second_password : return first_password
    else :
        print("Inserted Passwords don't match ! \n")
        return False


def encrypt_file(filepath) :
    password = False
    while(not password) :
        password = encrypt_password()
    key = scrypt(password, salt, key_len=32, N=2**17, r=8, p=1)
    out_filepath = get_out_filepath(filepath)
    try :
        with open(filepath , "rb") as file_in , open(out_filepath ,"wb") as file_out :
            file_out.write(salt)  # Write the salt to the top of the output file
            cipher = AES.new(key, AES.MODE_GCM)  # Create a cipher object to encrypt data
            file_out.write(cipher.nonce)  # Write out the nonce to the output file under the salt
            data = file_in.read(BUFFER_SIZE)
            while len(data) != 0:
                encrypted_data = cipher.encrypt(data)
                file_out.write(encrypted_data) 
                data = file_in.read(BUFFER_SIZE)
            tag = cipher.digest()
            file_out.write(tag)
    except : print("Something went wrong :( ")
    global status
    status = True

def decrypt_file(filepath ) :
    password = getpass("Insert your password : \n")
    decrypted_filepath = get_decrypted_filepath(filepath)
    try :
        with open(filepath , "rb") as file_in , open(decrypted_filepath ,"wb") as file_out :
            salt = file_in.read(32)
            key = scrypt(password, salt, key_len=32, N=2**17, r=8, p=1)
            nonce = file_in.read(16)  # The nonce is 16 bytes long
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            file_in_size = os.path.getsize(filepath)
            encrypted_data_size = file_in_size - 32 - 16 - 16  # Total - salt - nonce - tag = encrypted data
            for _ in range(int(encrypted_data_size / BUFFER_SIZE)):  # Identify how many loops of full buffer reads we need to do
                data = file_in.read(BUFFER_SIZE)  # Read in some data from the encrypted file
                decrypted_data = cipher.decrypt(data)  # Decrypt the data
                file_out.write(decrypted_data)  # Write the decrypted data to the output file
            data = file_in.read(int(encrypted_data_size % BUFFER_SIZE))  # Read whatever we have calculated to be left of encrypted data
            decrypted_data = cipher.decrypt(data)  # Decrypt the data
            file_out.write(decrypted_data)  # Write the decrypted data to the output file
            # Verify encrypted file was not tampered with
            tag = file_in.read(16)
            try:
                cipher.verify(tag)
            except ValueError as e:
                file_in.close()
                file_out.close()
                os.remove(decrypted_filepath)
                raise e
    except : print("something went wrong during decryption !")
    global status
    status = True

def secure_delete(filename):
        with open(filename , "ba+") as delfile:
            length = delfile.tell()
            for i in range(10):
                delfile.seek(0)
                delfile.write(os.urandom(length))
        os.remove(filename)

def check_file(filepath) :
    if os.path.isfile(filepath) : return filepath
    elif os.path.isdir(filepath) :
        if filepath.endswith('/') :
            filepath = filepath[:-1]
        suffix = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        file_archive = filepath + suffix
        shutil.make_archive(file_archive , 'zip', filepath)
        for root, dirs, files in os.walk(filepath):
            for filename in files:
                secure_delete(os.path.join(root, filename))
        shutil.rmtree(filepath)
        return file_archive + ".zip"
    else : return False

def main():
    my_parser = argparse.ArgumentParser(prog='aes_crypt',
                                        description='Matrix \'s program for enc/decrypting files and folders with AES256 GCM mode',
                                        usage='%(prog)s [options] path/file',
                                        epilog='Enjoy the program! :)')
    my_parser.add_argument('filepath', action='store', metavar='filepath', type=str,
                           help='the file or directory to be encrypted or decrypted')
    parser_group = my_parser.add_mutually_exclusive_group()
    parser_group.add_argument('-c', '--crypt', action='store_true', help='set mode to encrypt the file or directory')
    parser_group.add_argument('-d', '--decrypt', action='store_true', help='set mode to decrypt the file or directory')
    args = my_parser.parse_args()
    values = vars(args)
    filepath = values["filepath"]
    try :
        myfilepath = check_file(filepath)
        if not myfilepath : 
            print("Inserted filepath does not exists :(")
            return 1
    except : print("something went wrong ...")
    if values["crypt"] :
        encrypt_file(myfilepath)
        if status :
            secure_delete(myfilepath)
    if values["decrypt"] :
        decrypt_file(myfilepath)
        if status :
            os.remove(myfilepath)

if __name__ == "__main__" : main()