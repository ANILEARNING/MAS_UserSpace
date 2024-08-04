import streamlit as st
from streamlit_option_menu import option_menu
import about
import account
import home

# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import match_analyzer
import matchups
import chatbot
import resumeAnalyzer
import consultants

st.set_page_config(
    page_title="Mad About Sports - User Space",
    layout="wide"
)

#

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
                options=['Home', 'Chat Assistant', 'Resume Analyzer', 'Match Analyzer','Match Ups','Experts','About'],
                default_index=0,
            )

        # Run selected app
        if app == "Home":
            home.app()
        elif app == "Chat Assistant":
            if st.session_state.useremail:
                chatbot.main()
            else:
                st.info("Please log in to access the Chat Assistant.")
        elif app == "Resume Analyzer":
            if st.session_state.useremail:
                resumeAnalyzer.main()
            else:
                st.info("Please log in to access the Resume Analyzer.")
        elif app == "Match Analyzer":
            if st.session_state.useremail:
                match_analyzer.main()
            else:
                st.info("Please log in to access the Match Analyzer.")

        elif app == "Match Ups":
            if st.session_state.useremail:
                matchups.main()
            else:
                st.info("Please log in to access the Match Ups.")
        elif app == "Experts":
            if st.session_state.useremail:
                consultants.main()
            else:
                st.info("Please log in to access the Consultants Page.")

        elif app == "About":
            about.app()

# Create instance of MultiApp
multi_app = MultiApp()

# Add apps to MultiApp
multi_app.add_app("Home", home.app)
multi_app.add_app("About", about.app)

# Run MultiApp
multi_app.run()
