import streamlit as st
import sqlite3
import qrcode
import io
import base64
from PIL import Image

DATABASE = '/Users/noahfabricius/Desktop/adbis/src/samples.db'

def get_request_names():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT request_name FROM samples")
    request_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return request_names

def get_samples_by_request_name(request_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT eln_number, concentration FROM samples WHERE request_name = ?", (request_name,))
    samples = cursor.fetchall()
    conn.close()
    return samples

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Streamlit app
st.title("QR Code Generator for Samples")

# Fetch unique request names
request_names = get_request_names()

if request_names:
    # Dropdown menu for selecting a request name
    selected_request_name = st.selectbox("Select a project (request name):", request_names)
    
    # Fetch samples for the selected request name
    samples = get_samples_by_request_name(selected_request_name)

    if samples:
        for eln_number, concentration in samples:
            qr_content = f"ELN Number: {eln_number}, Concentration: {concentration}"
            st.write(f"Generating QR code for: {qr_content}")
            
            # Generate QR code
            qr_image = generate_qr_code(qr_content)
            
            # Convert QR code image to base64
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Convert QR code image to bytes for Streamlit display
            qr_image_bytes = buffer.getvalue()
            
            # Display QR code
            st.image(qr_image_bytes, caption=f"QR Code for ELN: {eln_number}", use_container_width=True)
            
            # Provide download link for the QR code
            href = f'<a href="data:image/png;base64,{img_base64}" download="qr_code_{eln_number}.png">Download QR Code</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.write("No samples found for the selected project.")
else:
    st.write("No projects found in the database.")