import ftplib
import functools
import os
import socket
from getpass import getpass


def safe_exec(fun):
    @functools.wraps(fun)
    def wrapper_safe_exec(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except ftplib.error_temp:
            print("A temporary error occurred")
            print("Please try this action later")
        except ftplib.error_perm as e:
            print(e)
        except Exception as e:
            print('Unexpected error occurred')
            print(e)

    return wrapper_safe_exec


class FTPU:

    def __init__(self):
        self.ftp = None
        self.path = 'ERROR'
        self.uname = 'ERROR'
        self.service = 'ERROR'
        self.commands = {func: getattr(self, func) for func in dir(self) if
                         callable(getattr(self, func)) and not func.startswith("__") and not func.startswith('_')}
        self._startup()

    @safe_exec
    def _startup(self):
        print("FTP Utility by to_matih")
        url = input("Enter the server url/ip: ")
        try:
            ftp = ftplib.FTP(url)
            self.service = url
        except socket.gaierror:
            print("Couldn't find given server")
            return
        username = input("Enter username(blank for anonymous): ")
        if username:
            self.uname = username
            password = getpass(prompt="Enter password: ")
            try:
                print(ftp.login(username, password))
            except ftplib.error_temp:
                print("A temporary error occurred")
                print("Please try later")
                return
            except ftplib.error_perm as e:
                print(e)
                return
        else:
            try:
                print(ftp.login())
                self.uname = 'Anonymus'
            except ftplib.error_perm:
                print("Server doesn't allow anonymous logging")
                return
            except ftplib.error_temp:
                print("A temporary error occurred")
                print("Please try later")
                return

        print(ftp.getwelcome())
        self.path = ftp.pwd()
        self.ftp = ftp

    def q(self):
        """Exit the program and close the connection
        usage: q"""
        print("Exiting program")
        print(self.ftp.quit())
        quit()

    @safe_exec
    def ls(self):
        """List files in current directory
        usage: ls"""
        print(self.ftp.dir())

    @safe_exec
    def cd(self, path):
        """Change current directory
        usage: cd {directory}"""
        self.ftp.cwd(path)
        self.path = self.ftp.pwd()

    @safe_exec
    def rm(self, file):
        """Removes a file
        usage: rm {file}"""
        self.ftp.delete(file)

    @safe_exec
    def rmd(self, directory):
        """Removes a directory
        usage: rm {directory}"""
        self.ftp.rmd(directory)

    @safe_exec
    def mkd(self, name):
        """Creates a directory
        usage: mkd {directory}"""
        self.ftp.mkd(name)

    @safe_exec
    def rnm(self, old, new):
        """Renames a file
        usage: rnm: """
        self.ftp.rename(old, new)

    def help(self, cm=None):
        """Show help message
        usage: help {command}"""
        if cm:
            if cm in self.commands:
                print("Help for {}".format(cm))
                print(self.commands[cm].__doc__)
            else:
                print('Unknown command')
                print("Type 'h' for a full list of commands")
        else:
            print("Available commands")
            template = "{:5s} {}"
            for com in self.commands:
                print(template.format(com, self.commands[com].__doc__.split('\n')[0]))

    @safe_exec
    def get(self, filename):
        """Downloads a file from server
        usage: get {filename}"""
        path = os.path.join(os.path.expanduser('~'), 'Downloads', filename)
        with open(path, 'wb') as f:
            self.ftp.retrbinary('RETR ' + filename, f.write)

    @safe_exec
    def cat(self, filename):
        """Prints the contents of a file
        usage: cat {filename}"""

        def cat_helper(data):
            print(data.decode('utf-8'))

        self.ftp.retrbinary('RETR ' + filename, cat_helper)

    @safe_exec
    def send(self, filepath):
        """Uploads a file from given path
        usage: upload {local_filepath}"""
        if not os.path.isfile(filepath):
            print("File not found")
            return
        with open(filepath, 'rb') as f:
            self.ftp.storbinary('STOR {}'.format(f.name), f)

    @safe_exec
    def replace(self, filename, old, new):
        """Replaces string in a given file
        usage: replace {filename} {to_replace} {replacement}"""

        def replace_helper(data):
            data = data.decode('UTF-8')
            data = data.replace(old, new)
            with open('tmp.txt', 'w') as f:
                f.write(data)

        self.ftp.retrbinary('RETR {}'.format(filename), replace_helper)
        with open('tmp.txt', 'rb') as fi:
            self.ftp.storbinary('STOR {}'.format(filename), fi)
        os.remove('tmp.txt')
