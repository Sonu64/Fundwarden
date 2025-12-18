from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('auth/register.html')

# Register route
@app.route("/register")
def register():
    return render_template('auth/register.html')

# Login route
@app.route("/login")
def login():
    return render_template('auth/login.html')

if __name__ == '__main__':
    app.run(debug=True)