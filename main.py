import streamlit as st

def handle_confirm():
    st.session_state.location = st.session_state.temp_location
    st.session_state.confirmed = True

# Main function to run the Streamlit app
def main():
    # Check if the location is already stored in session state
    if "location" not in st.session_state:
        st.title("Welcome to the Chemist App")
        # Store selection in temporary state variable
        st.session_state.temp_location = st.radio(
            "Select your location:", 
            ["Måløv 🔴", "Bagsværd 🔵"],
            key="location_radio"
        )
        st.button("Confirm", on_click=handle_confirm)
    elif "confirmed" in st.session_state and st.session_state.confirmed:
        # Step 2: Filter pages and guide based on stored location
        location = st.session_state.location
        if location == "Måløv 🔴":
            with st.sidebar:
                st.page_link('main.py', label='🏠 Guide')
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/4_insertresults.py', label='🔴 Insert Results')
                st.page_link('pages/5_library.py', label='📚 Library')

            st.subheader("As a chemist in Måløv 🔴")
            st.text("1. Upon receiving the package, open the Shipping Status page from the sidebar and update the project to 'Received'")
            st.text("2. Open the Insert Results page from the sidebar and follow the instructions")

        elif location == "Bagsværd 🔵":
            with st.sidebar:
                st.page_link('main.py', label='🏠 Guide')
                st.page_link('pages/1_createsample.py', label='🔵 Create Sample')
                st.page_link('pages/2_generateqr.py', label='🔵 Generate QR Code')
                st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
                st.page_link('pages/5_library.py', label='📚 Library')

            st.subheader("As a chemist in Bagsværd 🔵")
            st.text("1. Open the Create Sample page from the sidebar and follow the instructions")
            st.text("2. Open the Generate QR Code page from the sidebar and follow the instructions")
            st.text("3. Pack the samples and send them to Måløv")
            st.text("4. Open the Shipping Status page from the sidebar and update the project to 'Shipped'")

            # Automatically confirm the location if it's already selected but not confirmed
if "location" in st.session_state and "confirmed" not in st.session_state:
    st.session_state.confirmed = True

if __name__ == "__main__":
    main()

