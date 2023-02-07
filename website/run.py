from upsmash import create_full_app
from upsmash import db

app = create_full_app()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
