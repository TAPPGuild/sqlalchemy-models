"""
A preprocessor script that helps 'make schemas' generate json schemas.
"""
import json
from sqlalchemy_login_models import model
import alchemyjsonschema as ajs

factory = ajs.SchemaFactory(ajs.SingleModelWalker)


for name in model.__all__:
    base = getattr(model, name)
    print "generating schema for %s" % base.__tablename__
    schemaf = "sqlalchemy_login_models/schemas/%s.json" % (base.__tablename__)
    f = open(schemaf, 'w')
    schema = factory.__call__(base)
    f.write(json.dumps(schema))
    f.close()

