from sqlalchemy import create_engine

from backend.lib import sql_queries

# config = {'username': 's3_label_admin',
#           'password': 's3_label_admin;',
#           'ip': 'localhost',
#           'database_name': 's3_label'}

config = {'username': 'postgres',
          'password': 'postgres',
          'ip': 'localhost',
          'database_name': 's3_label'}

engine = create_engine('postgresql://{}:{}@{}:5432/{}'.format(config['username'],
                                                              config['password'],
                                                              config['ip'],
                                                              config['database_name']))

df = sql_queries.get_all_images(1, engine)
df2 = sql_queries.count_total_images(1, engine)
df3 = sql_queries.get_unlabeled_images(1, engine, 3)

print('test')
