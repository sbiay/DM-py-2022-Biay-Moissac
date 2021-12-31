from app.comutTest import test
from app import appliMoissac

app = appliMoissac.app

if __name__ == "__main__" and not test:
    app.run(debug=True)
else:
    print("Attention ! classes.py est en mode test")