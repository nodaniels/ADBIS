import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set Streamlit to use wide screen layout
st.set_page_config(layout="wide")

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
    sender_email = "testinglabmb@gmail.com"  # Din e-mailadresse
    sender_password = "rezrgeiaglpkcnoz"        # Din e-mailadgangskode
    subject = f"Statusopdatering for {request_name}"
    body = f"Status for '{request_name}' er blevet opdateret til: {status}."

    # Opret e-mailen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send e-mailen
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Brug Gmail SMTP-server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"E-mail sendt til {recipient_email}")
    except Exception as e:
        print(f"Fejl ved afsendelse af e-mail: {e}")

# Save the shipping status to the database
def save_shipping_status(request_name, status):
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
    selected_request = st.selectbox("Vælg en forespørgsel:", request_names)

    # Radio buttons for setting the status
    status = st.radio("Sæt status for forespørgslen:", ["Afsendt", "Modtaget"])

    # Input field for recipient email
    recipient_email = st.text_input("Indtast modtagerens e-mailadresse:", value="", max_chars=100)

    # Save the status when the button is clicked
    if st.button("Bekræft status"):
        if not recipient_email:
            st.error("Du skal indtaste en e-mailadresse.")
        else:
            save_shipping_status(selected_request, status)
            st.success(f"Status for '{selected_request}' er sat til '{status}' og gemt i databasen.")
else:
    st.warning("Ingen forespørgsler fundet i databasen.")

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
st.subheader("Oversigt over forsendelsesstatus")
shipping_entries = fetch_shipping_entries()
if shipping_entries:
    st.table(shipping_entries)
else:
    st.info("Ingen forsendelsesdata fundet i databasen.")