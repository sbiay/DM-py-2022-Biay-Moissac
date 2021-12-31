from warnings import warn

SECRET_KEY = "Bot !"

if SECRET_KEY == "Bot !":
    warn("Le secret par défaut n'a pas été changé !", Warning)