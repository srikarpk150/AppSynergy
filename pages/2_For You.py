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

def logout():
    st.session_state.signout = False
    st.session_state.signedout = False
    st.session_state.redirected = False
    st.session_state.preference = False
    st.session_state.username = ''
    st.session_state.email_input = ''
    st.session_state.password_input = ''

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

css = """
<style>
table {
    font-family: Arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    background-color: transparent;
    border: none; /* Remove border */
}

th {
    background-color: transparent;
    text-align: left;
    border: none; /* Remove border */
}

td {
    border: none; /* Remove border */
    padding: 8px;
}

tr:nth-child(even) {
    background-color: transparent;
}
</style>
"""


if not st.session_state.signout:
    switch_page("Login")
else:
    st.sidebar.button("Logout",on_click=logout)

def read_data():
    conn = sqlite3.connect('project.db')
    df = pd.read_sql_query("SELECT * FROM apps;", conn)
    conn.close()
    return df

def save_data():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    username = st.session_state.username
    if len(options) == 0:
        st.session_state.preference = False
    for i in options:
        sql = 'INSERT INTO user_pref (username, preference) VALUES (?, ?);'
        values = (username,i)
        c.execute(sql, values)
        conn.commit()
    conn.close()

def edit_pref():

    conn = sqlite3.connect('user.db')
    c= conn.cursor()
    sql = "DELETE FROM user_pref WHERE username = ?;"
    um = st.session_state.username
    value = (um,)
    c.execute(sql,value)
    conn.commit()
    conn.close()
    st.session_state.preference = False
    #st.experimental_rerun()

conn = sqlite3.connect('user.db')
df = pd.read_sql_query(f"SELECT * FROM user_pref WHERE username = '{st.session_state.username}';", conn)
conn.close()

if len(df) == 0:

    app_data = read_data()
    options = st.multiselect(
        'What is your Genre preference', app_data['Primary_Genre'].unique())
    
    if len(options) != 0:
        st.write('You selected:', options)

        st.text('Do you want to save your preference ?')

        st.button('Save',on_click = save_data)

else:

    conn = sqlite3.connect('user.db')
    df = pd.read_sql_query(f"SELECT * FROM user_pref WHERE username = '{st.session_state.username}';", conn)
    conn.close()

    preference = ', '.join(df['preference'])
    st.header(f"Your Preference - :red[{preference}]")

    if len(df['preference']) != 0:
        st.session_state.preference = True

    st.button('Edit your preference',on_click = edit_pref)

conn = sqlite3.connect('user.db')
df = pd.read_sql_query(f"SELECT * FROM user_pref WHERE username = '{st.session_state.username}';", conn)
conn.close()

if len(df)!=0:
    st.session_state.preference = True

if st.session_state.preference == False:

    if len(options) == 0:
        st.text('Please select your preferences')

else:
    st.header('Trending apps around you :')

    conn = sqlite3.connect('project.db')
    for i in df['preference']:
        query = f"SELECT * FROM TopRatedAppsByGenre WHERE Primary_Genre = '{i}' LIMIT 10;"
        top_rated_df = pd.read_sql_query(query, conn)
        
        st.subheader(f"Trending Apps in :red[{i}]")
        st.table(top_rated_df)
    conn.close()

    st.header('Best Free apps :')
    conn = sqlite3.connect('project.db')
    for i in df['preference']:

        query = f"SELECT App_Name, Developer FROM FreeApps WHERE Primary_Genre = '{i}' LIMIT 10;"
        top_rated_df = pd.read_sql_query(query, conn)
        
        st.subheader(f"Free Apps in :red[{i}]")
        st.table(top_rated_df)
    conn.close()






