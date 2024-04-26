import streamlit as st
import streamlit as st
import pandas as pd
import time
import sqlite3
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(
page_title="AppSynergy",
)

st.sidebar.title(':red[AppSynergy]')
st.markdown(
    """
     <style>
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.3) !important; /* Change the last value (0.5) to adjust opacity */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "signedout" not in st.session_state:
    st.session_state["signedout"] = False
if 'signout' not in st.session_state:
    st.session_state['signout'] = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'password' not in st.session_state:
    st.session_state.password = ''
if 'preference' not in st.session_state:
    st.session_state.preference = False
if 'redirected' not in st.session_state:
    st.session_state.redirected = False

#st.title('Welcome to :black[AppSynergy]')

st.markdown("<h1 style='display: inline;'>Welcome to <span style='color:Red;'>AppSynergy</span></h1>", unsafe_allow_html=True)


page_bg_img = f"""
<style>
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

@st.cache_data 
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data 
def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('background.jpg')


def forget():
    username = st.text_input('Username')
    new_password = st.text_input('New Password',type='password')
    old_password = st.text_input('Old Password',type='password')
    if st.button('Reset Password'):
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute('Select * FROM user_details WHERE username = ? and password = ?', (username, old_password))
        data = c.fetchall()
        if len(data) != 0:
            print(username, old_password)
            c.execute('UPDATE user_details SET password = ? WHERE username = ? and password = ?', (new_password, username, old_password))
            conn.commit()
            conn.close()
            st.success('Password Reset Successfull!')
            st.balloons()
        else:
            st.warning('Password Reset Failed')

def logout():
    st.session_state.signout = False
    st.session_state.signedout = False
    st.session_state.redirected = False
    st.session_state.preference = False
    st.session_state.username = ''
    st.session_state.email_input = ''
    st.session_state.password_input = ''

if st.session_state.signout:
    st.sidebar.button("Logout",on_click=logout)

def login(um,pw):
    conn = sqlite3.connect('user.db')
    query = 'SELECT * FROM user_details WHERE username = ? AND password = ?;'
    df = pd.read_sql_query(query, conn, params=(um, pw))
    
    if len(df) != 0:
        st.session_state.signedout = True
        st.session_state.signout = True
        query = 'SELECT email FROM user_details WHERE username = ?;'
        email = pd.read_sql_query(query, conn, params=(um,))
        st.session_state.email = email['email'].iloc[0]
        conn.close()
    else:
        st.warning('Login Failed')
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''
        st.session_state.email = ''
        st.session_state.password = ''

    return 

if not st.session_state["signedout"]:
    choice = st.selectbox('Login/Signup',['Login','Sign up','Reset Password'])

    if choice == 'Sign up':
        email = st.text_input('Email Address')
        password = st.text_input('Password',type='password')
        username = st.text_input("Enter Your Unique Username")
        st.session_state.username = username
        st.session_state.email = email
        st.session_state.password = password
        
        if st.button('Create my account'):

            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            #c.execute('DELETE FROM user_details;')
            query = 'SELECT username FROM user_details WHERE username = ?;'
            user = pd.read_sql_query(query, conn, params=(username,))

            query = 'SELECT email FROM user_details WHERE email = ?;'
            user_email = pd.read_sql_query(query, conn, params=(email,))

            conn.close()

            if len(user) != 0 and len(user_email) == 0:
                st.error("Please select a different username!")
            elif len(user_email) != 0:  
                    st.error("User already exists!")                  
            else:
                conn = sqlite3.connect('user.db')
                c = conn.cursor()
                sql = "INSERT INTO user_details (username, password, email) VALUES (?, ?, ?);"
                values = (username,password,email)
                c.execute(sql, values)
                conn.commit()
                conn.close()

                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
    
    elif choice == 'Login' :
        username = st.text_input('Username')
        password = st.text_input('Password',type='password')
        st.session_state.username = username
        st.session_state.password = password
        
        on_click = lambda: login(username, password)          
        st.button('Login', on_click = on_click)
    else:
        forget()

if st.session_state.signout:
            st.text('You have Successfully logged in')
            st.text('Name '+st.session_state.username)
            st.text('Email id: '+st.session_state.email)
            st.button('Log out', on_click=logout)

            if st.session_state.redirected == False:
                st.session_state.redirected = True
                time.sleep(0.2)
                switch_page('Home')
                






























