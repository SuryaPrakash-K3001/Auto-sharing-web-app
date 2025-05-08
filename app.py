from flask import Flask, request, render_template
from openpyxl import Workbook, load_workbook
import os
import requests

app = Flask(__name__)
EXCEL_FILE = 'rides.xlsx'
ULTRAMSG_INSTANCE_ID = 'instance114129'
ULTRAMSG_TOKEN = 'ukyr87apjysdlgd7'

# Create Excel file if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    wb = Workbook()
    ws = wb.active
    ws.append(['Name', 'Whatsapp', 'Departure', 'Destination', 'Timing'])
    wb.save(EXCEL_FILE)

def send_whatsapp_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send message:", e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('whatsapp')
    departure = request.form.get('departure')
    destination = request.form.get('destination')
    time = request.form.get('timing')

    if not all([name, phone, departure, destination, time]):
        return "All fields are required."

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    matched = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[2] == departure and row[3] == destination and row[4] == time:
            matched = {
                "name": row[0],
                "phone": row[1]
            }
            break

    ws.append([name, phone, departure, destination, time])
    wb.save(EXCEL_FILE)

    if matched:
        msg = f"You have a ride partner!\nName: {matched['name']}\nPhone: {matched['phone']}"
        send_whatsapp_message(phone, msg)
        reverse_msg = f"You have a ride partner!\nName: {name}\nPhone: {phone}"
        send_whatsapp_message(matched['phone'], reverse_msg)
        return "Match found and message sent to both users."
    else:
        return "Data saved. We will notify you when a match is found."

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

