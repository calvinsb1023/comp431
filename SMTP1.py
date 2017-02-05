import sys, os


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
    end = pos -1
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

    #return 250  # 250 OK
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
    start = pos+1
    pos = check_forward_path(s, pos)
    end = pos-1
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


# Processes the message into files
def process_message(MAIL_FROM, RCPT_TO, DATA):
    for receiver in RCPT_TO:
        direct = "forward/"

        # Create the 'forward directory' if it doesn't exist
        if not os.path.exists(direct):
            os.makedirs(direct)

        direct += receiver
        if os.path.exists(direct):
            append_write = 'a'  # append if the file exists
        else:
            append_write = 'w'  # write if the file doesn't exist

        with open(direct, append_write) as fwd_file:

            # Write mail from
            fwd_file.write('From: ' + MAIL_FROM + '\n')

            # Write all recipients
            for rcpt in RCPT_TO:
                fwd_file.write('To: ' + rcpt + '\n')

            for text in DATA:
                fwd_file.write(text)


def read_input():
    # Initializes state to look for MAIL FROM
    current_state = "MAIL_FROM"

    # Where we'll save our message information for each session
    MAIL_FROM = ""
    RCPT_TO = []
    DATA = []

    # Time to finally process it
    for line in sys.stdin:

        print line.rstrip('\n').lstrip()

        # If we're in the mail-from state
        if current_state == "MAIL_FROM":
            mail_from = check_mail_from_cmd(line)

            if mail_from == 500:
                print "500 Syntax error: command unrecognized"

            elif mail_from == 503:
                print "503 Bad sequence of commands"

            elif mail_from == 501:
                print "501 Syntax error in parameters or arguments"

            else:
                MAIL_FROM = mail_from
                current_state = "RCPT_TO"
                print "205 OK"

        # If we're in the rcpt-to state
        elif current_state == "RCPT_TO":
            rcpt_to = check_rcpt_to_cmd(line)

            if rcpt_to == 500:
                print "500 Syntax error: command unrecognized"

            elif rcpt_to == 503:

                if RCPT_TO and check_data_cmd(line) == 354:
                    current_state = "DATA"
                    print '354 Start mail input; end with <CRLF>.<CRLF>'

                else:
                    print "503 Bad sequence of commands"

            elif rcpt_to == 501:
                print "501 Syntax error in parameters or arguments"

            else:
                RCPT_TO.append(rcpt_to)
                print "250 OK"

        # If we're in the data state
        elif current_state == "DATA":
            if line == ".\n":
                print "250 OK"
                process_message(MAIL_FROM, RCPT_TO, DATA)

                # We reset the mail from, rcpt, and data
                MAIL_FROM = ""
                RCPT_TO = []
                DATA = []
            else:
                DATA.append(line)


read_input()
