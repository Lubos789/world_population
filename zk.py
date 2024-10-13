import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests



def api_info():
    api_endpoint = "https://api.openai.com/v1/chat/completions"
    api_key = st.secrets["auth_api_key"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    request_data = {
        "model": "gpt-3.5-turbo",  # Updated model version
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Write something interesting about this country: {selected_country}."}
        ],
        "max_tokens": 500,
        "temperature": 0.5,
    }

    response = requests.post(api_endpoint, headers=headers, json=request_data)

    if response.status_code == 200:
        response_text = response.json()["choices"][0]["message"]["content"]
        print(response_text)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.json())  # Print detailed error information

    return response_text

st.set_page_config(
    page_title="Europe Migration Dashboard",
    page_icon="",
    layout="wide")


# Načtení dat
data = pd.read_csv('data/population_tabel_csv.csv')

# Převod sloupců let na string, pokud ještě nejsou
data.columns = data.columns.astype(str)

col = st.columns((0.8, 1), gap='large', vertical_alignment='top')
with col[0]:
    # Výběr země
    countries = data['Country Name'].unique()
    selected_country = st.selectbox('Select a country', countries)

    # Filtr dat pro vybranou zemi
    country_data = data[data['Country Name'] == selected_country]

    # Graf trendu populace
    # st.subheader(f'Population Trend for {selected_country}')
    years = [str(year) for year in range(1960, 2023, 2)]
    population_values = country_data[years].values.flatten()

    # Ošetření chybějících hodnot nahrazením NaN
    population_values = [float(value) if value != '' else None for value in population_values]


    # Summary statistics
    st.subheader(f'Summary Statistics for {selected_country}')
    total_population = population_values[-1]
    average_growth = (population_values[-1] - population_values[0]) / len(years)
    st.write(f'Total population in 2022: {total_population:,.0f}')
    st.write(f'Average annual growth: {average_growth:,.0f}')

    # Vytvoření DataFrame pro trend populace
    population_trend = pd.DataFrame({
        'Year': years,
        'Population': population_values
    })

    # Zajištění, že sloupec 'Year' je typu string pro správné indexování
    population_trend['Year'] = population_trend['Year'].astype(str)

    # Vykreslení lineárního grafu pomocí Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=population_trend['Year'],
        y=population_trend['Population'],
        mode='lines+markers',
        name='Population'

    ))

    fig.update_layout(
        title=f'Population Trend for {selected_country}',
        xaxis_title='Year',
        yaxis_title='Population',
        xaxis=dict(tickmode='linear', tickangle=-45),
        template='plotly_white',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

with col[1]:
    # HTML and CSS code to center the subheader
    html_code = """
        <div style="text-align:center;">
            <h2>World Map</h2>
            <hr style="border:1px solid; width:80%; margin:auto; border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;">
        </div>
    """

    # Display the centered subheader
    st.markdown(html_code, unsafe_allow_html=True)

    # st.subheader("World Map", divider='rainbow')
    # Přidání sloupce pro zvýraznění vybrané země
    data['Selected Country'] = data['Country Name'] == selected_country

    # Nastavení barvy pro vybranou zemi
    data['Color'] = data['Selected Country'].apply(lambda x: 'blue' if x else 'lightgrey')

    # Vytvoření choropleth mapy
    fig_map = px.choropleth(
        data_frame=data,
        locations="Country Code",
        color="Color",
        hover_name="Country Name",
        hover_data={'Color': False, 'Country Code': False},
        color_discrete_map={'blue': 'blue', 'lightgrey': 'lightgrey'},
        labels={"Color": "Selected Country"}
    )
    fig_map.update_layout(coloraxis_showscale=False, template='plotly_dark', showlegend=False, height=670,)

    st.plotly_chart(fig_map)


if st.button("Click me to learn something about the country"):
    st.write(api_info())
