import streamlit as st
import webbrowser

def open_google_form():
    # Replace this URL with your actual Google Form URL
    form_url = "https://forms.gle/unPLDcbAi8JKmVjM9"
    webbrowser.open_new_tab(form_url)

def main():
    st.title("Welcome to Our Community Survey! 🌟")

    st.write("""
    ### We value your input! 💖
    
    Your opinions and experiences are incredibly important to us. 
    By sharing your thoughts, you're helping us create a better experience for everyone. 🙌
    
    Take a few minutes to fill out your suggestions and make your voice heard! 🗣️
    
    Your feedback will directly influence our future decisions and improvements. 🚀
    """)

    if st.button("Fill Out Now! 📝"):
        open_google_form()
        st.success("Thank you for participating! The survey form is opening in a new tab.")

