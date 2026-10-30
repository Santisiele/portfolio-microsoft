from core import dataverse_sql


def read_tds(env, query, params=None):
    return dataverse_sql(query, env, params)