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


# Streamlit app

def read_data():
    conn = sqlite3.connect('project.db')
    df = pd.read_sql_query("SELECT * FROM apps;", conn)
    conn.close()
    return df

app_data = read_data()

option = st.selectbox(
   "Which App Would You Like To :red[Rate]?",
   app_data['App_Name'].unique(),
   index=None,
   placeholder="Select any app...",
)

st.write('You selected: **<span style="color:red">{}</span>**'.format(option), unsafe_allow_html=True)

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


def save_data():
    global Reviews
    global Average_User_Rating
    global option

    conn = sqlite3.connect('user.db')
    query = f'SELECT * FROM user_review WHERE App_Name = "{option}" and username = "{st.session_state.username}";'
    df = pd.read_sql_query(query, conn)
    c = conn.cursor()    

    if len(df) == 0:
        sql = 'INSERT INTO user_review (username,app_name,rating) VALUES (?,?,?);'
        values = (st.session_state.username,option,rating)
        c.execute(sql, values)
        conn.commit()
        conn.close()

        conn2 = sqlite3.connect('project.db')
        c2 = conn2.cursor()
        Average_User_Rating = (int(Reviews) * float(Average_User_Rating) + int(rating)) / (int(Reviews) + 1)
        Reviews = int(Reviews) + 1
        query = 'UPDATE apps SET Average_User_Rating = ?, Reviews = ? WHERE app_name = ?;'
        values = (Average_User_Rating,Reviews,option)
        c2.execute(query, values)
        conn2.commit()
        conn2.close()

    else:

        sql = 'SELECT rating FROM user_review Where username = ? and app_name = ?'
        values = (st.session_state.username,option)
        c.execute(sql, values)
        initial_rating = c.fetchall()

        print(initial_rating[0][0],Average_User_Rating)
        
        conn2 = sqlite3.connect('project.db')
        c2 = conn2.cursor()
        if (int(Reviews) - 1) != 0:
            Average_User_Rating = (int(Reviews) * float(Average_User_Rating)  - float(initial_rating[0][0])) / (int(Reviews) - 1)
        else:
            Average_User_Rating = (int(Reviews) * float(Average_User_Rating)  - float(initial_rating[0][0]))

        Average_User_Rating = ((int(Reviews) -1 )* Average_User_Rating  + rating )/ int(Reviews)

        query = 'UPDATE apps SET Average_User_Rating = ? WHERE app_name = ?;'
        values = (Average_User_Rating,option)
        c2.execute(query, values)
        conn2.commit()
        conn2.close()

        sql = 'UPDATE user_review SET rating = ? WHERE username = ? and app_name = ? ;'
        values = (rating,st.session_state.username,option)
        c.execute(sql, values)
        conn.commit()
        conn.close()

    st.success('Review Saved Successfully!')

conn = sqlite3.connect('project.db')
query = f'SELECT * FROM apps WHERE App_Name = "{option}";'
df = pd.read_sql_query(query, conn)

conn.close()

Average_User_Rating = df['Average_User_Rating'].values
Reviews = df['Reviews'].values

df = df[['App_Name','Primary_Genre','Average_User_Rating','Target_Audience','Reviews']]

column_names_mapping = {
    'Primary_Genre': 'Genre',
    'App_Name': 'App',
    'Average_User_Rating':'User Rating',
    'Target_Audience':'Intended Audience'}

df = df.rename(columns=column_names_mapping)

if option is not None:
    st.markdown("<h3 style='text-align: center; color: white;'>App Details: </h3>", unsafe_allow_html=True)
    for column in df.columns:
        values = ', '.join(str(value) for value in df[column].values.tolist())
        st.write(f':red[{column}] - {values}')

    rating = st.slider("How would you rate this app on a scale of 0 to 5?", min_value=0, max_value=5)
    st.write(f"You selected: {option} and rated it {rating} out of 5.")

    st.button('Save',on_click = save_data)


conn = sqlite3.connect('user.db')
query = f'SELECT * FROM user_review WHERE username = "{st.session_state.username}";'
df = pd.read_sql_query(query, conn)
           

if len(df) != 0:

    st.header('Your :red[Reviews]')

    df = df[['app_name','rating']]

    column_names_mapping = {
    'app_name': 'App',
    'rating':'Your Rating'}

    df = df.rename(columns=column_names_mapping)

    st.table(df)

    st.header('Delete Your :red[Review]')
    conn = sqlite3.connect('user.db')
    query = f'SELECT app_name FROM user_review WHERE username = "{st.session_state.username}";'
    df2 = pd.read_sql_query(query, conn)

    name = st.selectbox("Which Rating Would You Like To :red[Delete]?",
                            df2['app_name'],
                            index = None,
                            placeholder="Select any app which you have reviewed...",)
    if st.button('Confirm') and name is not None:
        st.write('You selected: **<span style="color:red">{}</span>**'.format(name), unsafe_allow_html=True)
        query = f'SELECT rating FROM user_review WHERE username = "{st.session_state.username}" and app_name = "{name}";'
        r = pd.read_sql_query(query, conn)
        rating = r.values

        conn2 = sqlite3.connect('project.db')
        c2 = conn2.cursor()
        query = f'SELECT * FROM apps WHERE App_Name = "{name}";'
        df3 = pd.read_sql_query(query, conn2)

        Average_User_Rating = df3['Average_User_Rating'].values
        Reviews = df3['Reviews'].values

        if int(Reviews)!= 1:
            Average_User_Rating = (float(Average_User_Rating)*int(Reviews) - int(rating))/(int(Reviews) - 1)
        else:
            Average_User_Rating = (float(Average_User_Rating)*int(Reviews) - int(rating))
        Reviews = int(Reviews) - 1

        query = 'UPDATE apps SET Average_User_Rating = ?, Reviews = ? WHERE app_name = ?;'
        values = (Average_User_Rating,Reviews,name)
        c2.execute(query,values)
        conn2.commit()
        conn2.close()

        c= conn.cursor()
        query3 = f'DELETE FROM user_review WHERE username = "{st.session_state.username}" and app_name = "{name}";'
        c.execute(query3)
        conn.commit()
        conn.close()
        st.rerun()

