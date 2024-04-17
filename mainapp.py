from flask import Flask, render_template
import argparse
from io import StringIO
import sys

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
    parser = argparse.ArgumentParser(
        description="Example script to demonstrate argparse help.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50, width=100)
    )
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity.')
    parser.add_argument('-i', '--interface', type=str, help='Network interface to use.')

    # Capture the help output
    old_stdout = sys.stdout
    sys.stdout = help_file = StringIO()
    parser.print_help()
    sys.stdout = old_stdout
    help_content = help_file.getvalue()
    help_file.close()
    
    return render_template('help.html', help_content=help_content)