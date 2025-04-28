import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


st.set_page_config(layout="wide")

def main():

    with st.sidebar:
        st.page_link('main.py', label='Guide')
        st.page_link('pages/1_createsample.py', label='🔵 Create Sample')
        st.page_link('pages/2_generateqr.py', label='🔵 Generate QR Code')
        st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
        st.page_link('pages/4_insertresults.py', label='🔴 Insert Results')
        st.page_link('pages/5_library.py', label='📚 Library')


# Database connection setup
def create_connection():
    return sqlite3.connect("samples.db")
    # Set Streamlit to use wide screen layout
    
# Function to create the table if it doesn't exist
def create_table():
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
    conn.commit()
    cursor.close()
    conn.close()

# Function to insert data into the database
def insert_sample(initialer, sample_name, eln_number, project_name, concentration, method, comment, request_name):
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO samples (initialer, sample_name, eln_number, project_name, concentration, method, comment, request_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (initialer, sample_name, eln_number, project_name, concentration, method, comment, request_name))
    conn.commit()
    cursor.close()
    conn.close()

# Function to check if a request_name already exists
def request_name_exists(request_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM samples WHERE request_name = ?", (request_name,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

# Ensure the table is created
create_table()

# Streamlit app
st.title("Create Sample")

# Input for the sample request name
request_name = st.text_input("Enter a name for the sample request:", value="", max_chars=100)

# Ask user how many rows they want to create
num_rows = st.number_input("How many samples would you like to create?", min_value=1, step=1, value=1)

# Input for the receiver's email
receiver_email = st.text_input("Enter the receiver's email:", value="", max_chars=100)

# Initialize session state for samples
if "samples" not in st.session_state or len(st.session_state.samples) != num_rows:
    st.session_state.samples = [{"initialer": "", "sample_name": "", "eln_number": "", "project_name": "", "concentration": "", "method": "", "comment": ""} for _ in range(num_rows)]

samples = st.session_state.samples

# Render form for the specified number of rows
with st.form("sample_form"):
    for i, sample in enumerate(samples):
        st.write(f"Sample {i + 1}")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            sample["initialer"] = st.text_input(f"Initialer {i + 1}:", value=sample["initialer"], max_chars=10, key=f"initialer_{i}")
        with col2:
            sample["sample_name"] = st.text_input(f"Sample Name {i + 1}:", value=sample["sample_name"], max_chars=100, key=f"sample_name_{i}")
        with col3:
            sample["eln_number"] = st.text_input(f"ELN Number {i + 1}:", value=sample["eln_number"], max_chars=100, key=f"eln_number_{i}")
        with col4:
            sample["project_name"] = st.text_input(f"Project Name {i + 1}:", value=sample["project_name"], max_chars=100, key=f"project_name_{i}")
        with col5:
            sample["concentration"] = st.text_input(f"Concentration {i + 1}:", value=sample["concentration"], max_chars=100, key=f"concentration_{i}")
        with col6:
            sample["method"] = st.text_input(f"Method {i + 1}:", value=sample["method"], max_chars=100, key=f"method_{i}")
        with col7:
            sample["comment"] = st.text_input(f"Comment {i + 1}:", value=sample["comment"], max_chars=200, key=f"comment_{i}")
    submitted = st.form_submit_button("Submit")

def send_email_notification(request_name, recipient_email):
    sender_email = "testinglabmb@gmail.com"  # Din e-mailadresse
    sender_password = "rezrgeiaglpkcnoz"    # Din e-mailadgangskode
    subject = f"Sample Request: {request_name}"
    body = f"Hello, I have made a sample called {request_name} that will be sent to you shortly.\n\nBest regards,"

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


if submitted:
    if not request_name:
        st.error("Please provide a name for the sample request.")
    elif request_name_exists(request_name):
        st.error(f"The request name '{request_name}' already exists. Please choose a different name.")
    else:
        all_filled = True
        for sample in samples:
            if not all([sample["initialer"], sample["sample_name"], sample["eln_number"], sample["project_name"], sample["concentration"], sample["method"]]):
                all_filled = False
                break

        if all_filled:
            try:
                for sample in samples:
                    insert_sample(sample["initialer"], sample["sample_name"], sample["eln_number"], sample["project_name"], sample["concentration"], sample["method"], sample["comment"], request_name)
                st.success("Samples created successfully!")
                st.session_state.samples = [{"initialer": "", "sample_name": "", "eln_number": "", "project_name": "", "concentration": "", "method": "", "comment": ""} for _ in range(num_rows)]
                # Generate a message for the sample request
                # Send e-mail notification
                if receiver_email:
                    send_email_notification(request_name, receiver_email)
                    st.info(f"E-mail sent to {receiver_email}")
                else:
                    st.warning("No receiver email provided. E-mail not sent.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please fill in all required fields for all samples.")

if __name__ == "__main__":
    main()