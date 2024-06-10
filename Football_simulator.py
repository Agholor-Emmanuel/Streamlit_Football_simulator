import streamlit as st
import base64
import pandas as pd
import plotly.express as px
from PIL import Image
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
import io


def read_data(filepaths):
    df = pd.read_csv(filepaths)
    return df


def plot_match(df):
    pitch_length = 150  
    pitch_width = 120  
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#19cb13', line_color='white', pitch_length=pitch_length, pitch_width=pitch_width, 
                corner_arcs=True, stripe=True, stripe_color='#48da43')
    fig, ax = pitch.draw()
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
    image_data = buffer.getvalue()
    plt.close(fig)
    pitch_image = Image.open(io.BytesIO(image_data))
    
    def scale_df(df, pitch_length, pitch_width):
        min_x, max_x = df['x'].min(), df['x'].max()
        min_y, max_y = df['y'].min(), df['y'].max()
        df['x'] = (df['x'] - min_x) / (max_x - min_x) * pitch_length
        df['y'] = (df['y'] - min_y) / (max_y - min_y) * pitch_width
        return df
    
    df = scale_df(df, pitch_length, pitch_width)
    print (f'df is scaled {pd.Timestamp.now()}')
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='Team',
        symbol='Team',
        color_discrete_map={'home': 'red', 'away': '#0d8fed', 'ball':'#810ded'},
        symbol_map={'home': 'circle', 'away': 'circle', 'ball' : 'circle'},
        text='jerseyNum',
        #title='Player Positions on Football Field',
        animation_frame="frameNum",
        animation_group="jerseyNum", 
    )

    fig.update_traces(marker=dict(size=14))
    fig.update_traces(textfont=dict(size=8))
    print (f'first fig is done {pd.Timestamp.now()}')
    
    buffer = io.BytesIO()
    pitch_image.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read())

    fig.update_layout(
        autosize=False,
        width=1000,
        height=700,
        xaxis=dict(visible=False,autorange=False, range=[0, pitch_length], showgrid=False),
        yaxis=dict(visible=False,autorange=False, range=[0, pitch_width], showgrid=False )
    )
    fig.add_layout_image(
        dict(source='data:image/png;base64,{}'.format(img_str.decode()),
            xref='x',
            yref='y',
            x=0,
            y=0,
            sizex=150,
            sizey=120,
            xanchor="left",
            yanchor="bottom",
            sizing='stretch',
            opacity=0.9,
            layer='below')
    )
    fig.update_layout(template="plotly_white")
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 30
    #fig.show()
    return fig


def df_slider_filter(message, df):
    slider_selection = st.slider('%s' % (message), min(df['game_min']), max(df['game_min']), (0,3))
    min_time_batch = slider_selection[0]
    max_time_batch = slider_selection[1]
    return min_time_batch, max_time_batch
    
def main():
    st.set_page_config(page_title="Provispo Football Data Visuals", initial_sidebar_state='expanded')

    if "df" not in st.session_state:
        st.session_state.df = None
        print('start sessions 1')
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = None
        print('start sessions')
    # Load data if not loaded already
    if st.session_state.df is None:
        url = 'https://download2324.mediafire.com/dmkeaq22psogunHL0SOCKW1i0uOGv8z1H14sKbRJyWzArHRx1VCXQ3TMnEdFG2dlc616EmV8VyCJ5GngSu_xoi4Oh__8Sccr11R4r_IYYRVpSCb6uxkn2L5GW6qUSgIEr97RSKwVw66LNmrv-RRK6s4SkKEGJ5xf00SJas6PnHXtzLkUXQ/gmyitobgkzqw46c/final_data.csv'
        st.session_state.df = pd.read_csv(url, na_values = ['', ' '])
        #st.session_state.df = pd.read_csv(r"C:\Users\Emmanuel.Agholor\Documents\Provispo\venv\final_data.csv")
        print(f'df is loaded {pd.Timestamp.now()}')

    # # Filtered data initialization
    if st.session_state.filtered_df is None:
        st.session_state.filtered_df = st.session_state.df[(st.session_state.df['game_min'] >= 0) & (st.session_state.df['game_min'] <= 1)]
        print(f'filtered_df is loaded {pd.Timestamp.now()}')
        
    with st.sidebar: 
    #st.sidebar.header('Provispo `Visuals`') 
        st.subheader('Provispo `Visuals`') 
        with st.form(key='filter_form'):
            min_time_batch, max_time_batch = df_slider_filter('Select Time Range (mins)', st.session_state.df)
            submit_button = st.form_submit_button(label='Submit')
            
        #if st.button("Submit"):
        if submit_button:
            with st.spinner("Filtering data"):
                if max_time_batch - min_time_batch > 5:
                    max_time_batch = min_time_batch + 5
                st.session_state.filtered_df = st.session_state.df[(st.session_state.df['game_min'] >= min_time_batch) & (st.session_state.df['game_min'] <= max_time_batch)]
                print(f'df is filtered {pd.Timestamp.now()}')
                
    container_1 = st.container()
    with container_1:
        column_1, column_2 = st.columns([4, 1])
        with column_1:
            fig = plot_match(st.session_state.filtered_df)
            st.write(fig, width=1000)
        
if __name__ == "__main__":
    main()    
    
    

        
        
        
        
    
    
    
        
    

