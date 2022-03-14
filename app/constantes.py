from warnings import warn
from .comutTest import test

SECRET_KEY = "lessanglotslongsdesviolonsdelautomne"

ROWS_PER_PAGE = 10

if not test:
    if SECRET_KEY == "lessanglotslongsdesviolonsdelautomne":
        warn("Le secret par défaut n'a pas été changé !", Warning)
