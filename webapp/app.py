from flask import Flask, request, render_template_string
import subprocess
import os
import sys

# Add parent directory to Python path so bazi.py can find its modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from lunar_python import Lunar, Solar  # Verify lunar_python is accessible

app = Flask(__name__)

# HTML template with form
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <title>八字 (Bazi) Calculator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.css">
</head>
<body class="bg-gradient-to-br from-purple-50 to-indigo-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-md">
        <div class="bg-white rounded-xl shadow-xl p-8">
            <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">八字 (Bazi) Calculator</h1>
            
            <form method="POST" action="{{ url_for('calculate') }}" class="space-y-6">
                <div class="space-y-2">
                    <label for="datetime" class="block text-sm font-medium text-gray-700">Birth Date and Time</label>
                    <input type="text" id="datetime" name="datetime" placeholder="Select date and time..." class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white" required readonly>
                </div>
                
                <div class="space-y-2">
                    <label for="calendarType" class="block text-sm font-medium text-gray-700">Calendar Type</label>
                    <select id="calendarType" name="calendarType" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                        <option value="lunar">Lunar Calendar (农历)</option>
                        <option value="solar">Solar Calendar (阳历)</option>
                    </select>
                </div>
                
                <div class="space-y-2">
                    <label for="gender" class="block text-sm font-medium text-gray-700">Gender</label>
                    <select id="gender" name="gender" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                        <option value="male">Male (男)</option>
                        <option value="female">Female (女)</option>
                    </select>
                </div>
                
                <button type="submit" class="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors font-medium">
                    Calculate Birth Chart
                </button>
            </form>
            
            {% if result %}
            <div class="mt-8">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Results</h2>
                <pre class="bg-gray-50 p-6 rounded-lg overflow-x-auto text-sm font-mono">{{ result }}</pre>
            </div>
            {% endif %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/dist/flatpickr.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            flatpickr("#datetime", {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                time_24hr: true,
                defaultHour: 12,
                minuteIncrement: 1,
                minDate: "1900-01-01",
                maxDate: "2100-12-31",
                placeholder: "Select date and time...",
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get form data and parse datetime
        datetime_str = request.form['datetime']
        date_parts = datetime_str.split(' ')[0].split('-')
        time_parts = datetime_str.split(' ')[1].split(':')
        
        year = date_parts[0]
        month = date_parts[1]
        day = date_parts[2]
        hour = time_parts[0]
        calendar_type = request.form['calendarType']
        gender = request.form['gender']

        # Build command arguments using the current Python interpreter and ensure correct working directory
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bazi.py'))
        args = [sys.executable, script_path, year, month, day, hour]
        
        # Add options based on form selections
        if calendar_type == 'solar':
            args.append('-g')
        if gender == 'female':
            args.append('-n')

        # Run the bazi calculation with environment variables
        env = os.environ.copy()
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        env['PYTHONPATH'] = parent_dir
        result = subprocess.check_output(
            args,
            cwd=parent_dir,  # Run from parent directory where bazi.py is located
            stderr=subprocess.STDOUT,
            env=env
        ).decode('utf-8')

        return render_template_string(HTML_TEMPLATE, result=result)
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error calculating birth chart: {e.output.decode('utf-8')}"
        return render_template_string(HTML_TEMPLATE, result=error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        return render_template_string(HTML_TEMPLATE, result=error_message)

if __name__ == '__main__':
    app.run(debug=True)
