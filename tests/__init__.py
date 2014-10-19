import os
os.environ["SUPERGLOT_SETTINGS"] = 'config.testing'

import manage


def setup_package():
	manage.reset_schema()