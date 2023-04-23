from datetime import datetime, timedelta, timezone
from lib.db import db
# from opentelemetry import trace
# from lib.db import pool, query_wrap_array

# tracer = trace.get_tracer("home.activities")


class HomeActivities:
    def run(cognito_user_id=None):
        sql = db.template('activities', 'home')
        results = db.query_array_json(sql)
        return results
