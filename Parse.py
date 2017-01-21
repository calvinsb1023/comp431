def print_err(str):
    print 'ERROR -- ' + str


def check_mail_from_cmd(str):

    # Checks that the string starts with 'MAIL'
    if str[0:4] != 'MAIL':
        print_err('mail-from-command')
        return 0

    # Moves current position up 4 slots to check for at least one whitespace character
    pos = 4

    if len(str) < 5:
        print_err('mail-from-command')
        return 0
    if check_sp(str[pos]) == 0:
        print_err('mail-from-command')
        return 0
    pos += 1

    # Advances current position through any additional whitespace characters
    pos += advance_sp(str[pos:])

    # Checks for 'FROM:' string
    if str[pos:(pos+5)] != 'FROM:':
        print_err('mail-from-command')
        return 0

    # Advances positions 5 characters to whatever follows the colon and then advances through whitespace
    pos += 5

    offset = advance_sp(str[pos:])
    if offset >= 0:
        pos += offset
    else:
        print_err('mail-from-command')
        return 0

    # print str[pos:]
    # TODO: check reverse path instead
    if check_path(str, pos) == -1:
        print_err('path')
        return 0

    # TODO: Check nullspace
    # TODO: Check new line
    print 'Sender ok'
    return 1


def check_reverse_path(string, pos):
    # TODO: Check path
    return 0


def check_path(string, pos):
    if string[pos] != '<':
        print_err('path')
        return -1
    mb_offset = check_mailbox(string, pos)
    if mb_offset == -1:
        return -1
    pos += mb_offset
    if string[pos] != '>':
        print_err('path')
        return -1
    return 1


def check_mailbox(string, pos):
    offset = pos + check_local_part(string, pos)
    if offset == 0:
        print_err('local-part')
        return -1
    pos += offset
    if string[pos] != '@':
        print_err('mailbox')
        return -1
    pos += 1
    if check_domain(string, pos) == 0:
        print_err('domain')
        return -1
    return pos


def check_local_part(string, pos):
    # TODO: check string
    return 0

# TODO: fix
def check_domain(string, pos):
    offset = check_element(string, pos)
    if offset == 0:
        print_err('domain')
        return 0
    pos += offset

    if string[pos] == '.':
        pos += 1
        sub_offset = check_domain(string, pos)
        if sub_offset == 0:
            return 0
        return pos+sub_offset

    return pos


def check_element(string, pos):
    return check_name(string, pos)


# Returns name offset
def check_name(string, pos):
    if check_a(string[pos]) == 1:
        return 1 + check_let_dig_str(string, pos + 1)
    return 0


# returns string offset
def check_let_dig_str(string, pos):
    if check_let_dig(string[pos]) == 1:
        return 1 + check_let_dig_str(string, pos + 1)
    return 0


def check_let_dig(c):
    if check_a(c) == 1 or check_digit(c) == 1:
        return 1
    return 0


# Returns string offset
def check_string(string, pos):
    if check_char(string[pos]) == 1:
        return 1 + check_string(string, pos+1)
    return 0


def check_a(a):
    if a in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        return 1
    return 0


def check_char(c):
    return check_c(c)


def check_c(c):
    if 0 <= ord(c) < 128:
        if check_sp(c) == 0 and check_special(c) == 0:
            return 1
    return 0


def check_digit(d):
    if d in '0123456789':
        return 1
    return 0


def check_special(c):
    if c in '<>()[]\\.,;@"':
        return 1
    return 0


def check_crlf(c):
    if c == '\n':
        return 1
    return 0


# Checks for space and tab characters
def check_sp(c):
    if c == ' ' or c == '\t':
        return 1
    return 0


def advance_sp(string):
    offset = 0
    try:
        while check_sp(string[offset]) == 1:
            offset += 1
    except IndexError:
        offset = -1
    return offset


str_arr = ['MAIL FROM:<jeffay@cs.unc.edu>\n',
           'ma<jeffay@cs.unc.edu>\n',
           'MAIL  FROM:<jeffay@cs.unc.edu>\n',
           'MAIL FROM:jeffay@cs.unc.edu>\n',
           'MAILFROM:<jeffay@cs.unc.edu>\n']

for s in str_arr:
    print s
    check_mail_from_cmd(s)
