import streamlit as st

def app():
    st.title('Welcome to :orange[Mad About Sports]🏏')

    # Check if user is logged in
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    # Display login/signup form
    email = st.text_input('Email Address')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        # Validate login credentials (you can replace this with your actual validation logic)
        if email == 'test@mas.com' and password == 'password':
            st.session_state.useremail = email
            st.success('Successfully Logged In!')
        else:
            st.error('Invalid email or password. Please try again.')

    # if st.button('Sign Up'):
    #     # Implement signup logic here
    #     pass

    # Display logout button if user is logged in
    if st.session_state.useremail:
        if st.button('Sign Out'):
            st.session_state.useremail = ''
