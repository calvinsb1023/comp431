def print_err(s):
    print 'ERROR -- ' + s


def check_mail_from_cmd(s):
    # Checks for 'MAIL'
    if s[0:4] != 'MAIL':
        print_err('mail-from-cmd MAIL')
        return -1
    pos = 4

    # Checks for at least one white space
    try:
        pos += check_whitespace(s[pos])
    except IndexError:
        print_err('mail-from-cmd white_sp_1 index')
        return -1

    if pos == 4:
        print_err('mail-from-cmd white_sp_1')
        return -1

    # Advances through additional whitespace
    try:
        while check_whitespace(s[pos]) == 1:
            pos += 1
    except IndexError:
        print_err('mail-from-cmd whitespace_1_advance index')
        return -1

    # Check 'FROM:'
    if s[pos:pos+5] != 'FROM:':
        print_err('mail-from-cmd FROM:')
        return -1
    pos += 5

    # Advances through additional whitespace
    try:
        while check_whitespace(s[pos]) == 1:
            pos += 1
    except IndexError:
        print_err('mail-from-cmd whitespace_2_advance index')
        return -1

    # Checks the reverse path. If there's an error within path, assume path checker will handle the error
    pos = check_reverse_path(s, pos)
    if pos == -1:
        return -1

    # Advances through additional whitespace
    try:
        while check_whitespace(s[pos]) == 1:
            pos += 1
    except IndexError:
        print_err('mail-from-cmd pos_path_whitesp index')
        return -1

    if check_new_line(s[pos]) == 0:
        print_err('mail-from-cmd new_line')
        return -1
    print 'Sender ok'
    return 1


def check_reverse_path(s, pos):
    return check_path(s, pos)


def check_path(s, pos):
    # Check for '<'
    try:
        if s[pos] != '<':
            print_err('path <')
            return -1
    except IndexError:
        print_err('path < index')
        return -1
    pos += 1

    # Passes off to mailbox checker, assuming mailbox will report errors
    pos = check_mailbox(s, pos)
    if pos == -1:
        return -1

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
    if s[pos] != '@':
        print_err('mailbox')
        return -1
    pos += 1


    # TODO: check '@'
    # TODO: check domain
    return pos


def check_local_part(s, pos):
    return pos


def check_whitespace(c):
    if c == ' ' or c == '\t':
        return 1
    return 0


def check_new_line(c):
    if c == '\n':
        return 1
    return 0


mail_from_str_arr = ['MAIL FROM: <jeffay@cs.unc.edu>\n',
                     'MAIL\tFROM: ',
                     'MAIL    FROM:',
                     'MAIL \t FROM:',
                     '',
                     'MAIL FROM',
                     'MAIL',
                     'MAILFROM:']

for s in mail_from_str_arr:
    print s
    check_mail_from_cmd(s)
