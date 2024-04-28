from flask import Flask, render_template, jsonify, request, redirect, url_for
import threading

from ..util.scanner import Scanner
from ..config import Configuration
from ..args import Arguments


app = Flask(__name__)

scanner = Scanner()


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

@app.route('/scan', methods=['POST'])
def start_scan():
    
    # This should handle the scanning process in a non-blocking way
    thread = threading.Thread(target=scanner.find_targets)
    thread.start()
    return redirect(url_for('index'))

@app.route('/targets')
def show_targets():
    
    # Display available targets
    return render_template('targets.html', targets=scanner.targets)  # Create a targets.html template


# @app.route('/help')
# def help():
#     config = Configuration
#     args = Arguments(config)

#     help_text = args.get_help_text()
#     return render_template('help.html', help_text=help_text)

# @app.route('/run-command', methods=['POST'])
# def run_command():
#     import subprocess
    
#     # Running a command and capturing its output
#     try:
#         result = subprocess.run(['ping', '8.8.8.8'], capture_output=True, text=True)
#         # Sending the command output back as JSON
#         return jsonify({'output': result.stdout}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')