from superego.settings import config, BASE_DIR

database_file = BASE_DIR / config['sqlite']['filename']
connection_string = 'sqlite:///{}'.format(database_file)