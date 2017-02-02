import sys


def print_err(s):
    error = 'ERROR -- ' + s.rstrip()
    print error.rstrip().lstrip()


def check_mail_from_cmd(s):
    # Checks for 'MAIL'
    if s[0:4] != 'MAIL':
        print_err('mail-from-cmd')
        return -1
    pos = 4

    # Checks for at least one white space
    try:
        pos += check_whitespace(s[pos])
    except IndexError:
        print_err('mail-from-cmd')
        return -1

    if pos == 4:
        print_err('mail-from-cmd')
        return -1

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        print_err('mail-from-cmd')
        return -1

    # Check 'FROM:'
    if s[pos:pos+5] != 'FROM:':
        print_err('mail-from-cmd')
        return -1
    pos += 5

    # Advances through additional whitespace
    pos = advance_whitespace(s, pos)
    if pos == -1:
        print_err('mail-from-cmd')
        return -1

    # Checks the reverse path. If there's an error within path, assume path checker will handle the error
    pos = check_reverse_path(s, pos)
    if pos == -1:
        return -1

    # Advances through additional whitespace after the path
    pos = advance_whitespace(s, pos)
    if pos == -1:
        print_err('mail-from-cmd')
        return -1

    # Checks if there's a new line character
    try:
        if check_crlf(s[pos]) == 0:
            print_err('mail-from-cmd')
            return -1
    except IndexError:
        print_err('mail-from-cmd')
        return -1

    print 'Sender ok'
    return 1


def check_reverse_path(s, pos):
    return check_path(s, pos)


def check_path(s, pos):
    # Check for '<'
    try:
        if s[pos] != '<':
            print_err('path')
            return -1
    except IndexError:
        print_err('path')
        return -1
    pos += 1

    # Passes off to mailbox checker, assuming mailbox will report errors
    pos = check_mailbox(s, pos)
    if pos == -1:
        return -1

    # Check for '>'
    if s[pos] != '>':
        print_err('path')
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
            print_err('mailbox')
            return -1
    except IndexError:
        print_err('mailbox')
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
        print_err('local-part')
        return -1
    return pos + offset


def check_domain(s, pos):
    pos = check_element(s, pos)
    if pos == -1:
        print_err('domain')
        return -1
    if s[pos] == '.':
        pos = check_domain(s, pos + 1)
    return pos


def check_element(s, pos):
    return check_name(s, pos)


def check_name(s, pos):
    # TODO: handle index errors
    if check_a(s[pos]) == 1 and check_let_dig(s[pos+1]) == 1:
        pos += 1
        return check_let_dig_str(s, pos)
    return -1


def check_let_dig_str(s, pos):
    # TODO: handle index errors
    while check_let_dig(s[pos]) == 1:
        pos += 1
    return pos


def check_let_dig(c):
    if check_a(c) == 1 or check_digit(c) == 1:
        return 1
    return 0


# Returns the length of a valid string as an offset
def check_string(s, pos):
    # TODO: handle index error
    if check_c(s[pos]) == 1:
        return 1 + check_string(s, pos + 1)
    return 0


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


def check_crlf(c):
    if c == '\n':
        return 1
    return 0


for line in sys.stdin:
    print line.rstrip().lstrip()
    check_mail_from_cmd(line)
