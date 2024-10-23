from flask import Flask, render_template
from routes import main
from database import init_db

app = Flask(__name__)
init_db(app)

# Register the blueprint
app.register_blueprint(main)

@app.route('/')
def home():
    return render_template('main.index')

if __name__ == '__main__':
    app.run(debug=True)
