from flask import Flask, render_template, jsonify


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

@app.route('/help')
def help():
    from byteBuggy.config import Configuration
    from byteBuggy.args import Arguments

    Configuration.initialize(False)
    args_obj = Arguments(Configuration)
    args_dict = vars(args_obj.args)
    
    return render_template('help.html',  args=args_dict)

@app.route('/run-command', methods=['POST'])
def run_command():
    import subprocess
    
    # Running a command and capturing its output
    try:
        result = subprocess.run(['ping', '8.8.8.8'], capture_output=True, text=True)
        # Sending the command output back as JSON
        return jsonify({'output': result.stdout}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')