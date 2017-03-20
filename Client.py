import sys
import socket
import re


# Checks the "MAIL FROM:" command
def check_mail_from_cmd(s):

    # Checks that it's of type MAIL FROM
    pos = check_mail_from(s)

    if pos < 0:
        return check_recognized_command(s)

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Checks the reverse path. If there's an error within path, will report 501 here
    start = pos + 1
    pos = check_reverse_path(s, pos)
    end = pos - 1
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Advances through additional whitespace after the path
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Checks if there's a new line character
    try:
        if check_crlf(s[pos]) == 0:
            return 501  # 501 Syntax error in parameters or arguments
    except IndexError:
        return 501  # 501 Syntax error in parameters or arguments

    # return 250  # 250 OK
    return s[start:end]


# Checks that it's of type "MAIL FROM", returns adjusted position. Will return -1 if not of type MAIL FROM
def check_mail_from(s):
    # Checks for 'MAIL'
    if s[0:4] != 'MAIL':
        return -1
    pos = 4

    # Checks for at least one white space
    try:
        pos += check_whitespace(s[pos])
    except IndexError:
        return -1

    if pos == 4:
        return -1

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return -1

    # Check 'FROM:'
    if s[pos:pos + 5] != 'FROM:':
        return -1
    pos += 5
    return pos


# Checks "RCPT TO:" command
def check_rcpt_to_cmd(s):

    # Checks that it's of type rcpt_to
    pos = check_rcpt_to(s)

    # Will simply return -1 if not rcpt_to
    if pos < 0:
        return check_recognized_command(s)

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Checks the forward path. If there's an error within path, will report 501
    start = pos + 1
    pos = check_forward_path(s, pos)
    end = pos - 1
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Advances through additional whitespace after the path
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Checks if there's a new line character
    try:
        if check_crlf(s[pos]) == 0:
            return 501  # 501 Syntax error in parameters or arguments
    except IndexError:
        return 501  # 501 Syntax error in parameters or arguments

    return s[start:end]  # 250 OK


# Checks that it's of type "RCPT TO", returns adjusted position. Will return -1 if not of type RCPT TO
def check_rcpt_to(s):
    # Checks for 'RCPT'
    if s[0:4] != 'RCPT':
        return -1
    pos = 4

    # Checks for at least one white space
    try:
        pos += check_whitespace(s[pos])
    except IndexError:
        return -1

    if pos == 4:
        return -1

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return -1

    # Check 'TO:'
    if s[pos:pos + 3] != 'TO:':
        return -1
    pos += 3
    return pos


# Checks the DATA command, returns -1 if not data
def check_data_cmd(s):
    # Checks for 'DATA'
    pos = check_data(s)

    if pos < 0:
        check_recognized_command(s)

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        return 501  # 501 Syntax error in parameters or arguments

    # Checks if there's a new line character
    try:
        if check_crlf(s[pos]) == 0:
            return 501  # 501 Syntax error in parameters or arguments
    except IndexError:
        return 501  # 501 Syntax error in parameters or arguments

    return 354  # '354 Start mail input; end with <CRLF>.<CRLF>'


# Checks if command is of type DATA. Returns -1 if not, returns offset of 4 if it is
def check_data(s):
    if s[0:4] != 'DATA':
        return -1
    return 4


# Checks if it's a recognized command
def check_recognized_command(s):
    if check_mail_from(s) < 0 and check_rcpt_to(s) < 0 and check_data(s) < 0:
        return 500  # 500 Syntax error: command unrecognized
    return 503  # 503 Bad sequence of commands (potential)
    #return 1


def get_command_type(s):
    if check_mail_from(s) >= 0:
        return "MAIL_FROM"
    elif check_rcpt_to(s) >= 0:
        return "RCPT_TO"
    elif check_data(s) >= 0:
        return "DATA"
    else:
        return 500


def check_reverse_path(s, pos):
    return check_path(s, pos)


def check_forward_path(s, pos):
    return check_path(s, pos)


def check_path(s, pos):
    # Check for '<'
    try:
        if s[pos] != '<':
            return -1
    except IndexError:
        return -1
    pos += 1

    # Passes off to mailbox checker, assuming mailbox will report errors
    pos = check_mailbox(s, pos)
    if pos == -1:
        return -1

    # Check for '>'
    if s[pos] != '>':
        return -1

    pos += 1
    return pos


def check_mailbox(s, pos):
    # Check local part. Assume local part checker will report errors
    pos = check_local_part(s, pos)
    if pos == -1:
        return -1

    # Check for '@'
    try:
        if s[pos] != '@':
            return -1
    except IndexError:
        return -1
    pos += 1

    # Check domain. Assume domain checker will report errors
    pos = check_domain(s, pos)
    if pos == -1:
        return -1

    return pos


def check_local_part(s, pos):
    offset = check_string(s, pos)
    if offset <= 0:
        return -1
    return pos + offset


def check_domain(s, pos):
    pos = check_element(s, pos)
    if pos == -1:
        return -1
    if s[pos] == '.':
        pos = check_domain(s, pos + 1)
    return pos


def check_element(s, pos):
    return check_name(s, pos)


def check_name(s, pos):
    try:
        if check_a(s[pos]) == 1 and check_let_dig(s[pos+1]) == 1:
            pos += 1
            return check_let_dig_str(s, pos)
    except IndexError:
        return -1
    return -1


def check_let_dig_str(s, pos):
    try:
        while check_let_dig(s[pos]) == 1:
            pos += 1
        return pos
    except IndexError:
        return -1


def check_let_dig(c):
    if check_a(c) == 1 or check_digit(c) == 1:
        return 1
    return 0


def check_string(s, pos):
    try:
        if check_c(s[pos]) == 1:
            return 1 + check_string(s, pos + 1)
        return 0
    except IndexError:
        return -sys.maxint-1


def check_char(c):
    return check_c(c)


def check_c(c):
    if 0 <= ord(c) < 128:
        if check_whitespace(c) == 0 and check_special(c) == 0:
            return 1
    return 0


def check_a(a):
    if a in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        return 1
    return 0


def check_digit(d):
    if d in '0123456789':
        return 1
    return 0


def check_special(c):
    if c in '<>()[]\\.,;:@"':
        return 1
    return 0


def check_whitespace(c):
    if c == ' ' or c == '\t':
        return 1
    return 0


def advance_whitespace(s, pos):
    try:
        while check_whitespace(s[pos]) == 1:
            pos += 1
    except IndexError:
        pos = -1
    return pos


# Check for new line character
def check_crlf(c):
    if c == '\n':
        return 1
    return 0


# Generates a mail_from_cmd
def gen_from(s):
    return "MAIL FROM: <" + s.rstrip('\n') + '>\n'


# Generates a rcpt_to_cmd
def gen_to(s):
    return "RCPT TO: <" + s.rstrip('\n') + '>\n'


# Determines if a response is a success or not
def is_success(code, expected):

    filtered_code = int(re.search(r'\d+', code).group())
    return filtered_code == expected


# Prints output from a line and returns a state
def process_line(state, line):
    if state == "from":

        # Outputs mail-from-cmd
        sys.stdout.write(gen_from(line))

        # Reads response code
        message = sys.stdin.readline()

        # Echos response code
        sys.stderr.write(message)

        # If response if a success, we continue
        if is_success(message, 250):
            return "to"

        # If the response is not a success, we break and QUIT
        else:
            # sys.stdout.write("QUIT\n")
            return "broken"

    elif state == "to":

        # Outputs rcpt-to-cmd
        sys.stdout.write(gen_to(line))

        # Reads response code
        message = sys.stdin.readline()

        # Echos response code
        sys.stderr.write(message)

        # If response if a success, we continue
        if is_success(message, 250):

            # Sends the DATA cmd
            sys.stdout.write("DATA\n")

            # Reads response code
            message = sys.stdin.readline()

            # Echos response code
            sys.stderr.write(message)

            # If response if a success, we continue
            if is_success(message, 354):
                return "data"

            # If the response is not a success, we break and QUIT
            else:
                return "broken"

        # If the response is not a success, we break and QUIT
        else:
            return "broken"

    elif state == "data":
        if line[0:5] == "From:":

            # Prints a . with newline to signify end of message
            sys.stdout.write(".\n")

            # Reads response code
            message = sys.stdin.readline()

            # Echos response code
            sys.stderr.write(message)

            # If response if a success, we continue
            if is_success(message, 250):
                return "from"

            # If the response is not a success, we break and QUIT
            else:
                return "broken"
        else:
            sys.stdout.write(line)
            return "data"


def read_input(path):
    # States for the state machine include: "from", "to", "subject", "data", or "break"
    state = "from"

    f = open(path, 'r')

    for line in f:
        while True:
            state = process_line(state, line)
            if state != "from":
                break
        if state == "broken":
            break

    # If we've reached the end of file in the data state, try to feed a \n.\n
    if state == "data":
        sys.stdout.write(".\n")

        # Reads response code
        msg = sys.stdin.readline()

        # Echos response code
        sys.stderr.write(msg)

    # Regardless of whether or not the end of message file was successful, we'll print "QUIT"
    sys.stdout.write("QUIT\n")


def prompt_input(state, email):
    # States for the state machine include: "from", "to", "subject", "message", or "break"
    if state == "from":
        sys.stdout.write("From: ")
        mail_from_user = sys.stdin.readline().rstrip("\n")
        mail_fr = "<" + mail_from_user + ">"

        if check_reverse_path(mail_fr, 0) < 0:
            sys.stdout.write("There was a syntax error for '%s'. Please check and re-enter the address.\n" % mail_from_user)
            return "from"
        else:
            email.set_from(mail_fr)
            return "to"

    elif state == "to":
        sys.stdout.write("To: ")
        rcpt_to_user = sys.stdin.readline().rstrip("\n")
        rcpt_list = rcpt_to_user.replace(' ', '').split(',')

        broke = False

        for r in rcpt_list:
            r = r.rstrip()
            rcpt_str = "<" + r + ">"

            if check_reverse_path(rcpt_str, 0) < 0:
                sys.stdout.write("There was an error in the syntax for '%s'. "
                                 "Please check and re-enter the address.\n" % r)
                broke = True
            else:
                email.add_rcpt(rcpt_str)

        if broke:
            return "to"
        else:
            return "subject"

    elif state == "subject":
        sys.stdout.write("Subject: ")
        subject = sys.stdin.readline()
        email.set_subj(subject.rstrip())

        # Start message prompt
        sys.stdout.write("Message:\n")
        return "message"

    elif state == "message":
        line = sys.stdin.readline()
        if line == ".\n":
            return "ready"
        else:
            email.add_msg(line)
            return "message"


def send_data(email):

    # print "starting to send data"
    # Sets up socket interface
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Defines port number and server name to run on
    host_name = sys.argv[1]
    port_number = int(sys.argv[2])

    server_address = (host_name, port_number)

    # print "Waiting for connection"
    # Should be a 220 with server
    sock.connect(server_address)
    data = sock.recv(1024)
    # print data

    if is_success(data, 220):

        # Sends the HELO greeting
        helo = "HELO %s\n" % client_domain
        sock.send(helo)
        # print "Waiting for HELO ack"
        data = sock.recv(1024)
        # print "received: %s" % data

        if is_success(data, 250):
            msg = "MAIL FROM: " + email.get_from() + "\n"
            # print(msg)
            sock.sendall(msg)
            # print "Waiting for mail from ack"
            data = sock.recv(1024)
            # print "received: %s" % data

            if is_success(data, 250):
                for rcpt in email.get_rcpts():
                    msg = "RCPT TO: " + rcpt + "\n"
                    # print(msg)
                    sock.sendall(msg)
                    # print "Waiting for rcpt to ack"
                    data = sock.recv(1024)
                    # print "received: %s" % data

                    if not is_success(data, 250):
                        sys.stdout.write("There was a problem with RCPT TO: command - %s" % msg)
                        sock.close()

                msg = "DATA\n"
                sock.sendall(msg)
                # print msg
                data = sock.recv(1024)
                # print "received: %s" % data

                if is_success(data, 354):

                    # Write the Subject info
                    sock.send("Subject: " + email.get_subject() + "\n\n")

                    # Write the lines
                    for d in email.get_msg():
                        # print d
                        # print "sending: %s" % d
                        sock.send(d)

                    # End message
                    sock.send('.\n')
                    # print "Waiting for end of message ack"
                    data = sock.recv(1024)
                    # print "received: %s" % data
                    sock.send("QUIT")

                    if not is_success(data, 250):
                        sys.stdout.write("There was a problem sending the message data")
                        sock.close()
                        return -1
                    else:
                        # print "msg sent"
                        return 1

                else:
                    sys.stdout.write("There was a problem with DATA command")
                    sock.close()
                    return -1

            else:
                sys.stdout.write("There was a fatal problem with MAIL FROM: command - %s" % msg)
                sock.close()
                return -1
        else:
            sys.stdout.write("There was a fatal problem finalizing contact with the server.")
            sock.close()
            return -1
    else:
        sys.stdout.write("There was a fatal problem initializing contact with the server.")
        sock.close()
    return -1


# Helper class for sending mail
class Email(object):
    def __init__(self):
        self.mail_from = ""
        self.rcpt_to = []
        self.subject = ""
        self.msg = []

    def set_from(self, s):
        self.mail_from = s

    def get_from(self):
        return self.mail_from

    def add_rcpt(self, s):
        if s not in self.rcpt_to:
            self.rcpt_to.append(s)

    def get_rcpts(self):
        return self.rcpt_to

    def set_subj(self, s):
        self.subject = s

    def get_subject(self):
        return self.subject

    def add_msg(self, s):
        self.msg.append(s)

    def get_msg(self):
        return self.msg


if __name__ == "__main__":

    state = "from"
    client_domain = "classroom.cs.unc.edu"
    email = Email()
    # Get user input first
    while state != "ready":
        state = prompt_input(state, email)

    # print "made it out"
    send_data(email)
