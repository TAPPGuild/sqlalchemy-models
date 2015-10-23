"""
A preprocessor script that helps 'make schemas' generate json schemas.
"""
import json
from bitjws_login import model, db
import alchemyjsonschema as ajs

factory = ajs.SchemaFactory(ajs.SingleModelWalker)


for name in model.__all__:
    base = getattr(model, name)
    print "generating schema for %s" % base.__tablename__
    schemaf = "schemas/%s.json" % (base.__tablename__)                                           
    f = open(schemaf, 'w')
    schema = factory.__call__(base)
    f.write(json.dumps(schema))
    f.close()

