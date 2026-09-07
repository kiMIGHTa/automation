import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import schedule
import time
import logging
from pathlib import Path
import base64
import requests
import sqlite3

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This is a Python script for automating business tasks such as sending emails, SMS, and exporting data to Excel.
class BusinessAutomation:

    def __init__(self, config_file='config.json'):
        """Initialize the automation system with configuration"""
        self.config = self.load_config(config_file)
        self.setup_email_client()
        self.setup_sms_client()

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        downloads_path = str(Path.home() / "Downloads" / "BusinessExports")
        # Replace all data in the config file with your actual values
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "your-gmail-here",
                "password": "your-app-password-here"
            },
            "sms": {
                "provider": "bulksms",
                "username": "your-bulksms-username",
                "password": "your-bulk-sms-password",
                # i.e., "https://api.bulksms.com/v1/messages"
                "api_url": "bulksms-send-message-url-here"
            },
            "export": {
                "output_directory": downloads_path,
                "filename_prefix": "business_data"
            }
        }

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config file (config.json) if it doesn't exist
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created default config file: {config_file}")
            return default_config

    def setup_email_client(self):
        """Setup email client configuration"""
        self.email_config = self.config['email']

    def setup_sms_client(self):
        """Setup BulkSMS Kenya client"""
        try:
            self.sms_config = self.config['sms']
            logger.info("BulkSMS Kenya client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SMS client: {e}")
            self.sms_config = None

    def send_email(self, to_email, subject, body, attachment_path=None):
        """Send email with optional attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)

            # Connect to server and send email
            server = smtplib.SMTP(
                self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'],
                         self.email_config['password'])
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_sms(self, to_number, message):
        """Send SMS via BulkSMS Kenya API"""
        if not self.sms_config:
            logger.error("SMS client not initialized")
            return False

        try:
            # Prepare credentials
            credentials = f"{self.sms_config['username']}:{self.sms_config['password']}"
            encoded_credentials = base64.b64encode(
                credentials.encode('utf-8')).decode('utf-8')

            # Prepare headers and payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {encoded_credentials}"
            }

            payload = {
                "to": [to_number],
                "body": message,
                "encoding": "TEXT"  # or "UNICODE" for special characters
            }

            # Make the API request
            response = requests.post(
                self.sms_config['api_url'],
                json=payload,
                headers=headers
            )

            response.raise_for_status()
            logger.info(f"SMS sent successfully to {to_number}")
            return True

        except requests.exceptions.RequestException as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(f"Failed to send SMS to {to_number}: {error_detail}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return False

    def bulk_send_emails(self, email_list, subject, body, attachment_path=None):
        """Send emails to multiple recipients"""
        results = []
        for email in email_list:
            result = self.send_email(email, subject, body, attachment_path)
            results.append({'email': email, 'success': result})
            time.sleep(1)  # Rate limiting
        return results

    def bulk_send_sms(self, phone_list, message, delay=1):
        """Send SMS to multiple recipients"""
        results = []
        for phone in phone_list:
            result = self.send_sms(phone, message)
            results.append({'phone': phone, 'success': result})
            time.sleep(delay)  # Respect rate limits
        return results

    def create_sample_data(self):
        """Fetch data from database instead of hardcoded values"""
        try:
            # Connect to your database (SQLite example)
            conn = sqlite3.connect('business_automation.db')
            cursor = conn.cursor()

            # Fetch customer data
            cursor.execute("""
                SELECT 
                    customer_id AS Customer_ID,
                    name AS Name,
                    email AS Email,
                    phone AS Phone,
                    registration_date AS Registration_Date,
                    total_orders AS Total_Orders,
                    total_spent AS Total_Spent
                FROM customers
                LIMIT 3  
            """)
            customer_rows = cursor.fetchall()

            # Fetch agent data
            cursor.execute("""
                SELECT 
                    agent_id AS Agent_ID,
                    name AS Name,
                    email AS Email,
                    department AS Department,
                    hire_date AS Hire_Date,
                    sales_target AS Sales_Target,
                    sales_achieved AS Sales_Achieved,
                    performance_rating AS Performance_Rating
                FROM agents
            """)
            agent_rows = cursor.fetchall()

            # Fetch inventory data
            cursor.execute("""
                SELECT 
                    product_id AS Product_ID,
                    product_name AS Product_Name,
                    category AS Category,
                    price AS Price,
                    stock_quantity AS Stock_Quantity,
                    reorder_level AS Reorder_Level,
                    supplier AS Supplier,
                    last_updated AS Last_Updated
                FROM inventory
            """)
            inventory_rows = cursor.fetchall()

            # Convert to dictionary format matching original structure
            customer_data = {
                'Customer_ID': [row[0] for row in customer_rows],
                'Name': [row[1] for row in customer_rows],
                'Email': [row[2] for row in customer_rows],
                'Phone': [row[3] for row in customer_rows],
                'Registration_Date': [row[4] for row in customer_rows],
                'Total_Orders': [row[5] for row in customer_rows],
                'Total_Spent': [row[6] for row in customer_rows]
            }

            agent_data = {
                'Agent_ID': [row[0] for row in agent_rows],
                'Name': [row[1] for row in agent_rows],
                'Email': [row[2] for row in agent_rows],
                'Department': [row[3] for row in agent_rows],
                'Hire_Date': [row[4] for row in agent_rows],
                'Sales_Target': [row[5] for row in agent_rows],
                'Sales_Achieved': [row[6] for row in agent_rows],
                'Performance_Rating': [row[7] for row in agent_rows]
            }

            inventory_data = {
                'Product_ID': [row[0] for row in inventory_rows],
                'Product_Name': [row[1] for row in inventory_rows],
                'Category': [row[2] for row in inventory_rows],
                'Price': [row[3] for row in inventory_rows],
                'Stock_Quantity': [row[4] for row in inventory_rows],
                'Reorder_Level': [row[5] for row in inventory_rows],
                'Supplier': [row[6] for row in inventory_rows],
                'Last_Updated': [row[7] for row in inventory_rows]
            }

            return customer_data, agent_data, inventory_data

        except Exception as e:
            logger.error(f"Database error: {e}")
            # Fallback to sample data if DB fails
            return self._create_fallback_data()
        finally:
            conn.close()  # Ensure connection is always closed

    def _create_fallback_data(self):
        """Provide hardcoded sample data (fallback data) for demonstration"""
        customer_data = {
            'Customer_ID': ['C001', 'C002', 'C003'],
            'Name': ['Dennis Kimaita', 'Jane Smith', 'Bob Johnson'],
            'Email': ['dkimaita22@gmail.com', 'kimaitaduzit@gmail.com', 'devtest@ngkkenya.com'],
            'Phone': ['+254769375587', '+254746493184', '+254706397373'],
            'Registration_Date': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'Total_Orders': [5, 3, 8],
            'Total_Spent': [500.50, 299.99, 850.00]
        }

        agent_data = {
            'Agent_ID': ['A001', 'A002', 'A003', 'A004'],
            'Name': ['Sarah Connor', 'Mike Ross', 'Rachel Green', 'Harvey Specter'],
            'Email': ['sarah@company.com', 'mike@company.com', 'rachel@company.com', 'harvey@company.com'],
            'Department': ['Sales', 'Support', 'Marketing', 'Sales'],
            'Hire_Date': ['2023-01-10', '2023-03-15', '2023-05-20', '2023-02-28'],
            'Sales_Target': [10000, 8000, 12000, 15000],
            'Sales_Achieved': [12500, 7500, 13200, 16800],
            'Performance_Rating': [4.5, 4.2, 4.8, 4.9]
        }

        inventory_data = {
            'Product_ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'Product_Name': ['Laptop Pro', 'Wireless Mouse', 'Keyboard Mechanical', 'Monitor 24"', 'Headphones'],
            'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories'],
            'Price': [1299.99, 79.99, 149.99, 299.99, 199.99],
            'Stock_Quantity': [25, 150, 75, 40, 90],
            'Reorder_Level': [10, 50, 25, 15, 30],
            'Supplier': ['TechCorp', 'AccessoryPlus', 'KeyboardKing', 'DisplayMax', 'AudioTech'],
            'Last_Updated': ['2024-07-01', '2024-07-02', '2024-07-01', '2024-07-03', '2024-07-02']
        }
        return customer_data, agent_data, inventory_data

    def export_to_excel(self, data_dict, filename=None):
        """Export data to Excel with formatting"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config['export']['filename_prefix']}_{timestamp}.xlsx"

        # Create output directory if it doesn't exist
        output_dir = self.config['export']['output_directory']
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]

                # Apply formatting
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(
                    start_color="366092", end_color="366092", fill_type="solid")

                # Format headers
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        logger.info(f"Data exported to Excel: {filepath}")
        return filepath

    def auto_export_data(self):
        """Automatically export all business data"""
        try:
            # Get sample data (in real implementation, this would fetch from database)
            customer_data, agent_data, inventory_data = self.create_sample_data()

            data_dict = {
                'Customers': customer_data,
                'Agents': agent_data,
                'Inventory': inventory_data
            }

            filepath = self.export_to_excel(data_dict)

            # Send notification email about the export
            self.send_notification_email(filepath)

            return filepath

        except Exception as e:
            logger.error(f"Auto export failed: {e}")
            return None

    def send_notification_email(self, filepath):
        """Send notification email about data export"""
        try:
            subject = f"Automated Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            body = f"""
            Hello,
            
            The automated data export has been completed successfully.
            
            Export Details:
            - File: {os.path.basename(filepath)}
            - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            - Location: {filepath}
            
            Please find the exported data attached to this email.
            
            Best regards,
            Business Automation System
            """

            # Send to admin email (you can modify this)
            admin_email = self.email_config['email']
            self.send_email(admin_email, subject, body, filepath)

        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")

    def send_marketing_campaign(self, customer_data):
        """Send marketing campaign via email and SMS"""
        try:
            df = pd.DataFrame(customer_data)

            # Email campaign
            email_subject = "Special Offer - Don't Miss Out!"
            email_body = """
            Dear Valued Customer,
            
            We have an exclusive offer just for you!
            
            Get 20% off on your next purchase. Use code: SAVE20
            
            Offer valid until the end of this month.
            
            Shop now and save!
            
            Best regards,
            Your Store Team
            """

            email_results = self.bulk_send_emails(
                df['Email'].tolist(),
                email_subject,
                email_body
            )

            # SMS campaign
            sms_message = "Special Offer! Get 20% off with code SAVE20. Valid until month end. Shop now!"

            sms_results = self.bulk_send_sms(
                df['Phone'].tolist(),
                sms_message
            )

            logger.info(
                f"Marketing campaign sent - Emails: {len(email_results)}, SMS: {len(sms_results)}")

            return email_results, sms_results

        except Exception as e:
            logger.error(f"Marketing campaign failed: {e}")
            return [], []

    def run_weekly_marketing(self):
        """Run weekly marketing campaign"""
        customer_data, _, _ = self.create_sample_data()
        self.send_marketing_campaign(customer_data)

    def schedule_automated_tasks(self):
        """Schedule automated tasks"""
        # Schedule daily data export at 9 AM
        schedule.every().day.at("09:00").do(self.auto_export_data)

        # Schedule weekly marketing campaign on Mondays at 10 AM
        schedule.every().monday.at("10:00").do(self.run_weekly_marketing)

        logger.info("Automated tasks scheduled successfully")    

    def run_scheduler(self):
        """Run the task scheduler"""
        logger.info("Starting task scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Example usage
if __name__ == "__main__":
    # Initialize the automation system
    automation = BusinessAutomation()

    # Example 1: Send individual email
    print("1. Sending individual email...")
    automation.send_email(
        "your-email@email.com",
        "Test Subject",
        "This is a test email from the automation system."
    )

    # Example 2: Send individual SMS
    print("2. Sending individual SMS...")
    automation.send_sms("+254700000000", "Test SMS from automation system")

    # Example 3: Export data to Excel
    print("3. Exporting data to Excel...")
    filepath = automation.auto_export_data()
    print(f"Data exported to: {filepath}")

    # Example 4: Bulk email sending
    print("4. Sending bulk emails...")
    email_list = ['dkimaita22@gmail.com', 'kimaitaduzit@gmail.com']
    email_results = automation.bulk_send_emails(
        email_list,
        "Bulk Email Test",
        "This is a bulk email test."
    )
    print(f"Email results: {email_results}")

    # Example 5: Marketing campaign
    print("5. Running marketing campaign...")
    customer_data, _, _ = automation.create_sample_data()
    email_results, sms_results = automation.send_marketing_campaign(
        customer_data)

    # Example 6: Schedule automated tasks (uncomment to run)
    print("6. Starting automated scheduler...")
    automation.schedule_automated_tasks()
    automation.run_scheduler()

    print("All examples completed!")
