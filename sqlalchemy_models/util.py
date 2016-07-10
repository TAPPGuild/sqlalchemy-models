from sqlalchemy_models import user as um


def create_user(username, key, session):
    """
    Create a User and UserKey record in the session provided.
    Will rollback both records if any issues are encountered.
    After rollback, Exception is re-raised.

    :param username: The username for the User
    :param key: The public key to associate with this User
    :param session: The sqlalchemy session to use
    :rtype: User
    :return: the new User record
    """
    try:
        user = um.User(username=username)
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        session.flush()
        raise e
    try:
        ukey = um.UserKey(key=key, keytype='public', user_id=user.id)
        session.add(ukey)
        session.commit()
    except Exception as e:
        session.rollback()
        session.flush()
        session.delete(user)
        session.commit()
        raise e
    session.close()
    return user
