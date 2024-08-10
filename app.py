import logging
from flask import Flask, request, jsonify, render_template
from utils.google_sheets import load_google_sheet
from utils.email_utils import send_email_task
import pandas as pd

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load CSV data
def load_csv(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Email Blaster application!",
        "status": "success"
    })

@app.route('/upload_google_sheet', methods=['POST'])
def upload_google_sheet():
    logging.info("upload_google_sheet endpoint called")
    data = request.json
    logging.info(f"Received data: {data}")
    sheet_id = data['sheet_id']
    range_name = data['range_name']
    df = load_google_sheet(sheet_id, range_name)

    if df.empty:
        return jsonify({"message": "Failed to load Google Sheet data"}), 400

    for index, row in df.iterrows():
        logging.info(f"Queueing email to: {row['Email']} for company: {row['Company']}")
        send_email_task.delay(row['Email'], row['Company'])

    return jsonify({"message": "Emails are being sent"}), 200

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    logging.info("upload_csv endpoint called")
    file = request.files['file']
    df = load_csv(file)

    if df.empty:
        return jsonify({"message": "Failed to load CSV data"}), 400

    for index, row in df.iterrows():
        logging.info(f"Queueing email to: {row['Email']} for company: {row['Company']}")
        send_email_task.delay(row['Email'], row['Company'])

    return jsonify({"message": "Emails are being sent"}), 200

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    logging.info("manual_entry endpoint called")
    data = request.json
    logging.info(f"Received data: {data}")
    company_name = data['company_name']
    emails = data['emails']

    for email in emails:
        logging.info(f"Queueing email to: {email} for company: {company_name}")
        send_email_task.delay(email, company_name)

    return jsonify({"message": "Emails are being sent"}), 200

if __name__ == '__main__':
    app.run(debug=True)
