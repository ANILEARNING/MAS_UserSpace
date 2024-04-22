import streamlit as st
from streamlit_option_menu import option_menu
import about
import account
import home
# import chatbot
import resumeAnalyzer

st.set_page_config(
    page_title="Mad About Sports - User Space"
)

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append(
            {
                "title": title,
                "function": function
            }
        )

    def run(self):
        # Check if user is logged in
        if 'useremail' not in st.session_state:
            st.session_state.useremail = ''

        with st.sidebar:
            # Display login UI if user is not logged in
            if not st.session_state.useremail:
                account.app()
            else:
                st.write(f"Logged in as: {st.session_state.useremail}")
                if st.button('Sign Out'):
                    st.session_state.useremail = ''

            # Display app navigation
            app = option_menu(
                menu_title="Mad About Sports - User Space",
                options=['Home', 'Chat Assistant', 'Resume Analyzer', 'About'],
                default_index=0,
            )

        # Run selected app
        if app == "Home":
            home.app()
        elif app == "Chat Assistant":
            if st.session_state.useremail:
                resumeAnalyzer.main()
            else:
                st.info("Please log in to access the Chat Assistant.")
        elif app == "Resume Analyzer":
            if st.session_state.useremail:
                resumeAnalyzer.main()
            else:
                st.info("Please log in to access the Resume Analyzer.")
        elif app == "About":
            about.app()



# Create instance of MultiApp
multi_app = MultiApp()

# Add apps to MultiApp
multi_app.add_app("Home", home.app)
multi_app.add_app("About", about.app)

# Run MultiApp
multi_app.run()
