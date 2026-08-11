from core import dataverse_sql


def read_tds(env, query):
    return dataverse_sql(query, env)