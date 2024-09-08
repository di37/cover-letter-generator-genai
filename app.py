import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import os
import pandas as pd
from email_generator import chain, portfolio
from utils import clean_text

st.set_page_config(layout="wide", page_title="Cover Letter Generator", page_icon="📧")

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Sidebar for user input and file upload for csv file includes links of portfolios of the user
with st.sidebar:
    st.subheader("User Input")
    user_name = st.text_input("Enter your name:")

    uploaded_file = st.file_uploader(
        "Upload your CSV file (Tech Stack and Portfolio Link)", type="csv"
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
        st.dataframe(df.head())  # Display the first few rows of the uploaded data

        # Button to save the uploaded CSV file
        if user_name:
            # Use only the first name for the file name
            first_name = user_name.split()[0].lower().strip()
            save_path = os.path.join("data", f"my_portfolio_{first_name}.csv")

            if st.button("Save CSV File"):
                if os.path.exists(save_path):
                    st.warning(
                        f"A CSV file with the name 'my_portfolio_{first_name}.csv' already exists in the data folder."
                    )
                else:
                    df.to_csv(save_path, index=False)
                    st.success(f"CSV file saved as {save_path}")
                    portfolio.load_portfolio(file_name = f"my_portfolio_{first_name}.csv", df=df)
                    st.success(f"Portfolio loaded successfully to Chroma.")
        else:
            st.warning("Please enter your name to save the CSV file.")

st.title("📧 Cover Letter Generator")
url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
submit_button = st.button("Submit")

if submit_button:
    if not user_name:
        st.error("Please enter your name in the sidebar.")
    elif uploaded_file is None:
        st.error("Please upload your CSV file in the sidebar.")
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
            first_name = user_name.split()[0].lower().strip()
            collection_name = f"my_portfolio_{first_name}"
            
            try:
                links = portfolio.query_links(skills, collection_name=collection_name)
            except ValueError:
                st.error(f"Portfolio '{collection_name}' not found. Please save your CSV file first.")
                st.stop()

            # Show generated email(s)
            st.subheader("Generated Email")
            email = chain.write_mail(job, links)
            st.code(email, language="markdown")

        except Exception as e:
            st.error(f"An Error Occurred: {e}")