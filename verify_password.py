#!/usr/bin/env python3

'''
Do the logic for verifying tokens and passwords
'''

def verify_password(username, password, ip, cur, snaggy_logger):
    login_success = (False, {})

    available_password_sql = ''' select users.uid, token_expire_date
        from usertokens
        join users on usertokens.fk_uid = users.uid
        where token_expire_date >= NOW()
        and users.username = %s
        and tokentype = "PASSWORD"
        and activated = 1
        and token=SHA2(CONCAT(salt,%s),512)'''

    available_password_values = (username, password)

    try:
        cur.execute(available_password_sql, available_password_values)
        all_passwords = cur.fetchone()
    except Exception as error :
        snaggy_logger.warning("Failed Login attempt for User: '{}' from IP: '{}' with errror : {}".format(username, ip, str(error)))
        login_success = (False, {})
    else :
        if all_passwords == None :
            snaggy_logger.warning("Failed Login attempt for User: '{}' from IP: '{}' with incorrect password match.".format(username, ip))
            login_success = (False, {})
        else :
            # A correct Token
            snaggy_logger.debug("Successful login attempt for User: '{}' from IP: '{}'".format(username, ip))
            login_success = (True, all_passwords)

    return login_success
