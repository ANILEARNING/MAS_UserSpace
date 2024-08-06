import streamlit as st
import webbrowser

def main():

    st.markdown(
        """
        <style>
        .button {
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            text-decoration: none;
            color: white;
            background-color: #4CAF50;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            margin: 10px 2px;
        }

        .button:hover {
            background-color: #45a049; /* Darker green on hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title(" We value your input! 💖🌟")

    st.write("""
    Your opinions and experiences are incredibly important to us. 
    By sharing your thoughts, you're helping us create a better experience for everyone. 🙌
    
    Take a few minutes to fill out your suggestions and make your voice heard! 🗣️
    
    Your feedback will directly influence our future decisions and improvements. 🚀
    """)
    form_url = "https://forms.gle/unPLDcbAi8JKmVjM9"
    # Create a button-like link that opens the survey in a new tab
    st.markdown(f'<a href="{form_url}" target="_blank" class="button">Fill Out Now! 📝</a>', unsafe_allow_html=True)

    st.success("Thank you for participating! The survey form is opening in a new tab.")

