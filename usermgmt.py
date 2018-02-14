#!/usr/bin/env python3

'''
Do the logic for verifying tokens and passwords
'''

import random

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

def adduser(newusername, initialpassword, cur, snaggy_logger):

    '''
    This should only be called "by hand" by an administrator.

    Flow is check if username is a dupe.

    Add new User , then Set that User's Password.
    '''

    successfully_added = False

    check_user_exists_sql = ''' select users.uid from users where users.username = %s '''

    insert_new_user = ''' insert into users ( username ) values ( %s ) '''

    insert_new_password = ''' insert into
        usertokens ( token, tokentype, fk_uid, token_expire_date, salt, activated )
        VALUES ( SHA2(CONCAT(%s,%s),512), 'PASSWORD', %s, (NOW() + INTERVAL 365 DAY), %s, 1 )
        '''

    try:
        cur.execute(check_user_exists_sql)
        possible_user=cur.fetchall()
        amount_found = len(possible_users)
    except Exception as dupcheckerror :
        snaggy_logger.critical("Error doing duplication check: {}".format(str(dupcheckerror)))
        successfully_added = False
    else :
        # Continue With Insert
        new_user_args=[ str(username) ]
        try:
            cur.execute(insert_new_user, new_user_args)
            user_id = g.cur.lastrowid
        except Exception as newusererror :
            snaggy_logger.warning("Error inserting new user: {}".format(str(newusererror)))
            successfully_added = False
        else :
            # Set Initial Password

            # Generate My Random Salt
            salt_value = random.randint(0,4294967294)

            password_values = ( salt_value, password, user_id, salt_value )

            cur.execute(insert_new_password, password_values)


        
