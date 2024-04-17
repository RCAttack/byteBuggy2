from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')