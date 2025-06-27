import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set Streamlit to use wide screen layout
st.set_page_config(layout="wide")

def main():
    with st.sidebar:
        # Always show the Guide link at the top
        st.page_link('main.py', label='🏠 Guide')
        
        # Check location from session state
        if 'location' in st.session_state:
            if st.session_state.location == "Bagsværd 🔵":
                st.page_link('pages/1_createsample.py', label='🔵 Create Sample')
                st.page_link('pages/2_generateqr.py', label='🔵 Generate QR Code')
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/5_library.py', label='📚 Library')
            
            elif st.session_state.location == "Måløv 🔴":
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/4_insertresults.py', label='🔴 Insert Results')
                st.page_link('pages/5_library.py', label='📚 Library')
        else:
            st.warning("Please select your location on the main page")
            st.page_link('main.py', label='Go to main page')



# Page header
st.title("Shipping Status")
# Database connection setup
def create_connection():
    return sqlite3.connect("samples.db")

# Function to create the tables if they don't exist
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initialer TEXT NOT NULL,
            sample_name TEXT NOT NULL,
            eln_number TEXT NOT NULL,
            project_name TEXT NOT NULL,
            concentration TEXT NOT NULL,
            method TEXT NOT NULL,
            comment TEXT,
            request_name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_name TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Ensure the tables exist
create_tables()

# Fetch request names from the samples table
def get_request_names():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT request_name FROM samples")
    request_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return request_names

# Function to send an email notification
def send_email_notification(request_name, status, recipient_email):
    sender_email = "testinglabmb@gmail.com"  # Your email address
    sender_password = "rezrgeiaglpkcnoz"     # Your email password
    subject = f"Status Update for {request_name}"
    body = f"The status for '{request_name}' has been updated to: {status}."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Use Gmail SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Save the shipping status to the database
def save_shipping_status(request_name, status, recipient_email):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Delete older entries for the same request_name
    cursor.execute("""
        DELETE FROM shipping
        WHERE request_name = ?
    """, (request_name,))
    
    # Insert the new status
    cursor.execute("""
        INSERT INTO shipping (request_name, status)
        VALUES (?, ?)
    """, (request_name, status))
    
    conn.commit()
    conn.close()

    # Send an email notification
    send_email_notification(request_name, status, recipient_email)

# Dropdown menu for selecting a request
request_names = get_request_names()
if request_names:
    selected_request = st.selectbox("Select a request:", request_names)

    # Radio buttons for setting the status
    status = st.radio("Set the status for the request:", ["Shipped", "Received"])

    # Input field for recipient email
    recipient_email = st.text_input("Enter the recipient's email address:", value="", max_chars=100)

    # Save the status when the button is clicked
    if st.button("Confirm Status"):
        if not recipient_email:
            st.error("You must enter an email address.")
        else:
            save_shipping_status(selected_request, status, recipient_email)
            st.success(f"The status for '{selected_request}' has been set to '{status}' and saved in the database.")
else:
    st.warning("No requests found in the database.")

# Fetch all shipping entries sorted by timestamp (newest first)
def fetch_shipping_entries():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT request_name, status, timestamp
        FROM shipping
        ORDER BY timestamp DESC
    """)
    entries = cursor.fetchall()
    conn.close()
    return entries

# Display the shipping table
st.subheader("Shipping Status Overview")
shipping_entries = fetch_shipping_entries()
if shipping_entries:
    st.table(shipping_entries)
else:
    st.info("No shipping data found in the database.")

if __name__ == "__main__":
    main()