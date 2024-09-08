import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import os
import pandas as pd
from email_generator import chain, portfolio
from utils import clean_text

st.set_page_config(layout="wide", page_title="Cover Letter Generator", page_icon="📧")

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Initialize session state for storing manual entries and user name
if 'manual_entries' not in st.session_state:
    st.session_state.manual_entries = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

MAX_MANUAL_ENTRIES = 3

# Function to add entry and clear inputs
def add_entry():
    if st.session_state.techstack and st.session_state.link:
        st.session_state.manual_entries.append({
            'Techstack': st.session_state.techstack,
            'Links': st.session_state.link
        })
        st.session_state.techstack = ""
        st.session_state.link = ""
        st.success("Entry added successfully!")
    else:
        st.warning("Please enter both Techstack and Link.")

# Sidebar for user input
with st.sidebar:
    st.subheader("User Input")
    st.session_state.user_name = st.text_input("Enter your name:", value=st.session_state.user_name)

    # Option to manually input Techstack and links
    manual_input = st.checkbox("Manually input Techstack and links")
    
    if manual_input:
        if len(st.session_state.manual_entries) < MAX_MANUAL_ENTRIES:
            st.text_input("Enter your Techstack:", key="techstack")
            st.text_input("Enter a portfolio link:", key="link")
            
            st.button("Add Entry", on_click=add_entry)
        
        if st.session_state.manual_entries:
            st.write("Current entries:")
            for i, entry in enumerate(st.session_state.manual_entries):
                st.write(f"{i+1}. {entry['Techstack']} - {entry['Links']}")
        
        if len(st.session_state.manual_entries) >= MAX_MANUAL_ENTRIES:
            st.warning("You've reached the maximum number of manual entries. Please upload a CSV file for more entries.")
        
        if st.session_state.manual_entries:
            df = pd.DataFrame(st.session_state.manual_entries)
    
    if len(st.session_state.manual_entries) >= MAX_MANUAL_ENTRIES or not manual_input:
        uploaded_file = st.file_uploader(
            "Upload your CSV file (Tech Stack and Portfolio Link)", type="csv"
        )
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("CSV file uploaded successfully!")
            st.dataframe(df.head())  # Display the first few rows of the uploaded data

    # Button to save the data
    if st.session_state.user_name and ('df' in locals()):
        first_name = st.session_state.user_name.split()[0].lower().strip()
        save_path = os.path.join("data", f"my_portfolio_{first_name}.csv")

        if st.button("Save and Load Portfolio"):
            if os.path.exists(save_path):
                st.warning(
                    f"A CSV file with the name 'my_portfolio_{first_name}.csv' already exists in the data folder."
                )
            else:
                df.to_csv(save_path, index=False)
                st.success(f"Data saved as {save_path}")
                portfolio.load_portfolio(file_name=f"my_portfolio_{first_name}.csv", df=df)
                st.success(f"Portfolio loaded successfully to Chroma.")
                # Clear manual entries after saving
                st.session_state.manual_entries = []
    else:
        st.warning("Please enter your name and provide your portfolio data to save and load.")

# Main content
st.title("📧 Cover Letter Generator")
url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
submit_button = st.button("Submit")

if submit_button:
    if not st.session_state.user_name:
        st.error("Please enter your name in the sidebar.")
    elif 'df' not in locals():
        st.error("Please provide your portfolio data in the sidebar.")
    else:
        try:
            # Display loading animation while extracting the job
            with st.spinner("Extracting job details..."):
                # Load job data from URL
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)

                # Extract job details
                job = chain.extract_job(data)

            # Show extracted job information
            st.subheader("Extracted Job Information")
            st.json(job)  # Display job details in JSON format

            # Extract skills and query portfolio
            skills = job.get("skills", [])
            first_name = st.session_state.user_name.split()[0].lower().strip()
            collection_name = f"my_portfolio_{first_name}"
            
            try:
                links = portfolio.query_links(skills, collection_name=collection_name)
            except ValueError:
                st.error(f"Portfolio '{collection_name}' not found. Please save and load your portfolio data first.")
                st.stop()

            # Show generated email(s)
            st.subheader("Generated Email")
            email = chain.write_mail(job, links)
            st.code(email, language="markdown")

        except Exception as e:
            st.error(f"An Error Occurred: {e}")