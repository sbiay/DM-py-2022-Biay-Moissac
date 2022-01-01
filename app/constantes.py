from warnings import warn
from .comutTest import test

SECRET_KEY = "lessanglotslongsdesviolonsdelautomne"

if not test:
    if SECRET_KEY == "lessanglotslongsdesviolonsdelautomne":
        warn("Le secret par défaut n'a pas été changé !", Warning)
