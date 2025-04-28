import streamlit as st

# Main function to run the Streamlit app
def main():

    with st.sidebar:
        st.page_link('main.py', label='Guide')
        st.page_link('pages/1_createsample.py', label='🔵 Create Sample')
        st.page_link('pages/2_generateqr.py', label='🔵 Generate QR Code')
        st.page_link('pages/3_shippingstatus.py', label='🚐 Shipping Status')
        st.page_link('pages/4_insertresults.py', label='🔴 Insert Results')
        st.page_link('pages/5_library.py', label='📚 Library')

    st.title("Guide to use the app")
    
    
    col1, col2 = st.columns(2)
    with col1:

        st.subheader("As a chemist in Bagsværd 🔵")
        st.text("1. Open the Create Sample page from the sidebar and follow the instructions")
        st.text("2. Open the Generate QR Code page from the sidebar and follow the instructions")
        st.text("3. Pack the samples and send them to the Måløv")
        st.text("4. Open the Shipping Status page from the sidebar and update the project to 'Shipped'")

    with col2:

        st.subheader("As a chemist in Måløv 🔴")
        st.text("1. Upon receiving the package, open the Shipping Status page from the sidebar and update the project to 'Received'")
        st.text("2. Open the Insert Results page from the sidebar and follow the instructions")
      

if __name__ == "__main__":
    main()

    