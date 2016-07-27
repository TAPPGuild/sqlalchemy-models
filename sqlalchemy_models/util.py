import json

import alchemyjsonschema
from alchemyjsonschema import command

import broker as bm
import exchange as em
import todo
import user as um
import wallet as wm
from __init__ import LedgerAmount


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
    return user


def build_definitions(dpath="sqlalchemy_models/_definitions.json"):
    """
    Nasty hacky method of ensuring LedgerAmounts are rendered as floats in json schemas, instead of integers.

    :param str dpath: The path of the definitions file to create as part of the build process.
    """
    command.run(alchemyjsonschema.AlsoChildrenWalker, module=todo, outdir="sqlalchemy_models",
                relation_decision=alchemyjsonschema.RelationDesicion())
    definitions = ""
    for line in open(dpath, 'r'):
        definitions += line
    definitions = json.loads(definitions)
    newdef = open(dpath.replace("_def", "def"), 'w+')
    for name in definitions['definitions']:
        for mod in [um, em, wm, bm]:
            if hasattr(mod, name):
                model = getattr(mod, name)
                for attr in definitions['definitions'][name]['properties']:
                    if hasattr(getattr(model, attr).property, 'columns') and \
                            isinstance(getattr(model, attr).property.columns[0].type, LedgerAmount):
                        definitions['definitions'][name]['properties'][attr]['type'] = "number"
    newdef.write(json.dumps(definitions, indent=2))
    newdef.close()


def filter_query_by_attr(query, model, attrname, attr):
    if attr is not None:
        query = query.filter(getattr(model, attrname) == attr)
    return query


if __name__ == "__main__":
    build_definitions()
