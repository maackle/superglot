import os
os.environ["SUPERGLOT_SETTINGS"] = 'config.testing'

import manage


def setup_package():
	manage.rebuild_db()