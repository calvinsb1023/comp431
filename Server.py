
import os
import socket
import sys


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
            # print "error no newline"
            # return 501  # 501 Syntax error in parameters or arguments
            return s[start:end]  # attempt to fix it
    except IndexError:
        return 501  # 501 Syntax error in parameters or arguments

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
            # return 501  # 501 Syntax error in parameters or arguments
            return s[start:end]  # 250 OK
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
        # print "whitespace error"
        return 501  # 501 Syntax error in parameters or arguments

    # Checks if there's a new line character
    try:
        if check_crlf(s[pos]) == 0:
            # print "no newline error"
            s += '\n'
            return 354  # 501 Syntax error in parameters or arguments
    except IndexError:
        return 501  # 501 Syntax error in parameters or arguments

    return 354  # '354 Start mail input; end with <CRLF>.<CRLF>'


# Checks if command is of type DATA. Returns -1 if not, returns offset of 4 if it is
def check_data(s):
    if s[0:4] != 'DATA':
        return -1
    return 4


# Checks if command is of type HELO. Returns -1 if not, returns offset of 4 if it is
def check_helo(s):
    if s[0:4] != 'HELO':
        return -1
    return 4


# Checks if it's a recognized command
def check_recognized_command(s):
    if check_mail_from(s) < 0 and check_rcpt_to(s) < 0 and check_data(s) < 0 and check_helo(s):
        return 500  # 500 Syntax error: command unrecognized
    return 503  # 503 Bad sequence of commands (potential)


def check_end_of_data(s):

    if s == "." \
            or s == ".\n" \
            or s == ".\r\n" \
            or "\n.\n" in s:
        return True


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
    # print "Checking domain... %s" % s
    pos = check_element(s, pos)
    if pos == -1:
        return -1
    if pos < len(s) and s[pos] == '.':
        pos = check_domain(s, pos + 1)
    return pos


def check_element(s, pos):
    return check_name(s, pos)


def check_name(s, pos):
    # print "Checking name... %s" % s
    try:
        if check_a(s[pos]) == 1 and check_let_dig(s[pos+1]) == 1:
            # print "Name checked a and let dig, pos: %d" % pos
            pos += 1
            # print "Name checked a and let dig, pos: %d" % pos
            return check_let_dig_str(s, pos)
    except IndexError:
        # print "IndexError"
        return -1
    return -1


def check_let_dig_str(s, pos):
    try:
        while pos < len(s) and check_let_dig(s[pos]) == 1:
            # print "Checking let dig %s, pos: %d" % (s, pos)
            pos += 1
        return pos
    except IndexError:
        # print "Let-dig IndexError"
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


# Processes the message into files
def process_message(MAIL_FROM, RCPT_TO, DATA):
    for receiver in RCPT_TO:
        direct = "forward/"
        domain = receiver.split('@')[1]

        # Create the 'forward directory' if it doesn't exist
        if not os.path.exists(direct):
            os.makedirs(direct)

        direct += domain
        if os.path.exists(direct):
            append_write = 'a'  # append if the file exists
        else:
            append_write = 'w'  # write if the file doesn't exist

        with open(direct, append_write) as fwd_file:

            # Write mail from
            fwd_file.write('From: <' + MAIL_FROM + '>\n')

            # Write all recipients
            for rcpt in RCPT_TO:
                fwd_file.write('To: <' + rcpt + '>\n')

            for text in DATA:
                fwd_file.write(text)


def send_data(con, s):
    con.send(s)


def read_input(con):
    # Initializes state to look for MAIL FROM
    current_state = "MAIL_FROM"

    # Where we'll save our message information for each session
    MAIL_FROM = ""
    RCPT_TO = []
    DATA = []

    while True:
        # Time to finally process it
        line = con.recv(1024)

        if line == "QUIT\r\n" or line == "QUIT\n" or line == "QUIT":
            con.close()
            break

        # If we're in the mail-from state
        if current_state == "MAIL_FROM":

            mail_from = check_mail_from_cmd(line)

            if mail_from == 500:
                send_data(con, "500 Syntax error: command unrecognized\n")

            elif mail_from == 503:
                send_data(con, "503 Bad sequence of commands\n")

            elif mail_from == 501:
                send_data(con, "501 Syntax error in parameters or arguments\n")

            else:
                MAIL_FROM = mail_from
                current_state = "RCPT_TO"
                send_data(con, "250 %s... Sender ok\n" % mail_from)

        # If we're in the rcpt-to state
        elif current_state == "RCPT_TO":
            rcpt_to = check_rcpt_to_cmd(line)

            if rcpt_to == 500:
                send_data(con, "500 Syntax error: command unrecognized\n")

            elif rcpt_to == 503:

                if check_data_cmd(line) == 354:
                    current_state = "DATA"
                    send_data(con, '354 Start mail input; end with <CRLF>.<CRLF>\n')

                else:
                    send_data(con, "503 Bad sequence of commands (but inside rcpt_to) %d\n" % check_data_cmd(line))

            elif rcpt_to == 501:
                send_data(con, "501 Syntax error in parameters or arguments\n")

            else:
                RCPT_TO.append(rcpt_to)
                send_data(con, "250 %s... Recipient ok\n" % rcpt_to)

        # If we're in the data state
        elif current_state == "DATA":
            # str_arr = line.split('\n')

            # for c in line:
            #    print ord(c)

            # print "in data: %s" % line
            # sys.stdout.write(line + ' ' + '%d\n' % len(line))

            if check_end_of_data(line):
                # print "should be ending"
                if len(line) > 3:
                    str_arr = line.split('\n')
                    for substr in str_arr:
                        if substr.rstrip().lstrip() != '.':
                            DATA.append(substr.rstrip('\n') + '\n')
                        else:
                            break

                send_data(con, "250 OK msg end\n")
                current_state = "MAIL_FROM"
                process_message(MAIL_FROM, RCPT_TO, DATA)
            else:
                DATA.append(line)


if __name__ == "__main__":

    # Sets up socket interface
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Defines port number and server name to run on
    # host_name = 'classroom.cs.unc.edu'
    host_name = 'localhost'
    port_number = int(sys.argv[1])
    greeting_msg = "220 %s\n" % host_name

    # Sets up the socket and port
    port_bound = False
    client_name = ''
    while port_bound is not True:
        server_address = (host_name, port_number)
        try:
            sock.bind(server_address)
            port_bound = True
        # If the port is already busy, we'll try on the next port
        except socket.error:
            new_port = (port_number + 1) % 65535
            sys.stdout.write("\nERROR: Failed to bind to http://%s:%d/\nNow attempting http://%s:%d/" % (host_name, port_number, host_name, new_port))
            port_number = (port_number + 1) % 65535

    while True:
        # States will be listen, connected, receiving
        sock.listen(1)
        state = "listen"
        # print >> sys.stderr, "Server waiting on http://%s:%d/..." % (host_name, port_number)

        # Once connected, change state to connected
        state = "connected"
        connection, client_address = sock.accept()

        # print >> sys.stderr, 'Connection from', client_address
        connection.send("220 %s\n" % host_name)

        try:
            while True:

                # If we're in the connected state, we want to see a valid HELO command
                if state == "connected":
                    data = connection.recv(1024)

                    #sys.stdout.write(data)

                    if data == "QUIT\r\n" or data == "QUIT\n" or data == "QUIT":
                        state = "listening"
                        connection.close()

                    if check_helo(data) > 0:
                        # Splits expected HELO command into command and then domain
                        words = data.split()
                        if len(words) < 2:
                            msg = "501 HELO requires valid domain name\n"
                            connection.send(msg)
                        else:
                            dom_code = check_domain(words[1], 0)
                            if dom_code < 0:
                                msg = "501 HELO requires valid domain name\n"
                                connection.send(msg)
                            else:
                                client_name = words[1]
                                msg = "250 Hello, %s, pleased to meet you.\n" % client_name
                                state = "process"
                                connection.send(msg)

                    else:
                        code = check_recognized_command(data)
                        if code == 500:
                            msg = "500 Syntax error: command unrecognized\n"
                            connection.send(msg)

                        elif code == 503:
                            msg = "503 Bad sequence of commands\n"
                            connection.send(msg)

                elif state == "process":
                    read_input(connection)
                    state = "listen"
                    break

                else:
                    # print >> sys.stderr, 'sending data back to the client'
                    # connection.sendall("HELO")
                    # print >> sys.stderr, 'no more data from', client_address
                    break
        except socket.error:
            sys.stdout.write("Some sort of socket error happened...")

        # Clean up the connection
        connection.close()

