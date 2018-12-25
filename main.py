from core import FTPU


def main():
    ftp = FTPU()
    if not ftp.ftp:
        quit()
    while 1:
        c = input(ftp.ftp.pwd())
        c = c.split(' ')
        cm = c.pop(0)
        if cm in ftp.commands:
            if len(c):
                ftp.commands[cm](*c)
            else:
                try:
                    ftp.commands[cm]()
                except TypeError:
                    print('This command requires additional arguments')
                    print("Type 'help {}' to se it's usage".format(cm))
        else:
            print("Unknown command\nType 'help' to get available commands")


if __name__ == '__main__':
    main()
