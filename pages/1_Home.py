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
table.dataframe tr:nth-child(odd) {
    background-color: rgba(255, 255, 255, 0.5);
}

table.dataframe th, table.dataframe td {
    background-color: rgba(255, 255, 255, 0.5);
    color: rgba(0, 0, 0, 0.8);
    padding: 8px;
    border: none;
}

table.dataframe th {
    font-weight: bold;
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

def top_developers():
    conn = sqlite3.connect('project.db')
    top_dev_df = pd.read_sql_query("SELECT * FROM TopDevelopers LIMIT 10;", conn)
    conn.close()

    column_names_mapping = {
    'developer': 'Developer',
    'total_apps': 'Total Apps'}
    top_dev_df = top_dev_df.rename(columns=column_names_mapping)


    st.subheader("Top Developers by Total Apps Developed")
    st.table(top_dev_df)

# Function to display top-rated apps by genre
def top_rated_apps_by_genre(genre):
    conn = sqlite3.connect('project.db')
    query = f"SELECT * FROM TopRatedAppsByGenre WHERE Primary_Genre = '{genre}' LIMIT 10;"
    top_rated_df = pd.read_sql_query(query, conn)
    conn.close()

    column_names_mapping = {
    'Primary_Genre': 'Genre',
    'App_Name': 'App',
    'Average_User_Rating':'User Rating'}

    top_rated_df = top_rated_df.rename(columns=column_names_mapping)

    st.subheader(f"Top Rated {genre} Apps")
    st.table(top_rated_df)


def recent_releases():
    conn = sqlite3.connect('project.db')
    query = f"SELECT * FROM RecentlyReleased WHERE Primary_Genre = '{selected_genre}' LIMIT 10;"
    rr_df = pd.read_sql_query(query, conn)
    conn.close()

    column_names_mapping = {
    'App_Name': 'App',
    'Primary_Genre': 'Genre'}
    rr_df = rr_df.rename(columns=column_names_mapping)

    st.subheader(f"Recently Released Apps:")
    st.write(css, unsafe_allow_html=True)
    st.table(rr_df)

st.markdown("<h1 style='text-align: center; color: white;'>AppSynergy</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: white; font-family: Roboto;font-style: italic;'>Where Your Desires and Apps Unite in Harmony</h5>", unsafe_allow_html=True)

# Read data from SQLite database
app_data = read_data()


# Filter by Genre
selected_genre = st.selectbox("Select Genre to View Top Rated Apps", app_data['Primary_Genre'].unique())
#Recent Releases
recent_releases()
#Top rated by genre
top_rated_apps_by_genre(selected_genre)

# Slider for Average User Rating
min_rating = st.slider("Minimum Average User Rating", min_value=0, max_value=5, value=3)
app_data = app_data[app_data['Primary_Genre'] == selected_genre]
filtered_apps = app_data[app_data['Average_User_Rating'] >= min_rating].head(10)
filtered_apps = filtered_apps[['App_Name','Primary_Genre','Size_in_MB','Average_User_Rating']]

column_names_mapping = {
    'Primary_Genre': 'Genre',
    'App_Name': 'App',
    'Average_User_Rating':'User Rating',
    'Size_in_MB':'Size(in MB)'}

filtered_apps = filtered_apps.rename(columns=column_names_mapping)

# Display filtered apps
st.subheader(f"Apps with Minimum Average User Rating - {min_rating}")
st.table(filtered_apps.reset_index())

# Display top developers
top_developers()



conn = sqlite3.connect('project.db')
top_dev_df = pd.read_sql_query("SELECT developer FROM TopDevelopers;", conn)
dev = st.selectbox("Select Any Developer to View His Apps", top_dev_df,index = None)
if dev is not None:
    devid = pd.read_sql_query(f'SELECT DeveloperId FROM developers WHERE Developer ="{dev}" ;', conn)
    devid = devid.values[0][0]
    apps = pd.read_sql_query(f'SELECT * FROM apps WHERE DeveloperId = "{devid}";', conn)
    st.subheader(f"Apps Created by {dev}")
    st.table(apps)
    conn.close()

    
