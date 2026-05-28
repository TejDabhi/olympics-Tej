
import streamlit as st
import pandas as pd
import  preprocessor,helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

from helper import men_vs_female, prediction

df = pd.read_csv('olympics_dataset.csv')
region_df = pd.read_csv('noc_regions.csv')
df=preprocessor.process(df,region_df)
st.sidebar.title("Olympics Analysis ")
st.sidebar.image('https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_menu=st.sidebar.radio(
    'Select an Option',
    ('Medal Tally','Overall Analysis','Country-wise Analysis','Athlete-wise Analysis','Predictions')
)
# st.dataframe(df)
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")

    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Title logic
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} overall performance")
    else:
        st.title(f"{selected_country} performance in {selected_year} Olympics")

    # Display medal tally with visible Rank column
    st.table(medal_tally)

if user_menu=='Overall Analysis':
    editions=df['Year'].unique().shape[0] - 1
    cities=df['City'].unique().shape[0]
    sports=df['Sport'].unique().shape[0]
    events=df['Event'].unique().shape[0]
    athletes=df['Name'].unique().shape[0]
    nations=df['region'].unique().shape[0]
    st.title("Top Statistics")
    col1,col2,col3=st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)
    nations_over_time=helper.data_over_time(df,'region')
    fig = px.line(nations_over_time, x='Edition', y='region')
    st.title("Participating Nations over the year")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event')
    st.title("Events over the year")
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x='Edition', y='Name')
    st.title("Athletes over the year")
    st.plotly_chart(fig)

    st.title("No. of Events over time(Every Sport) ")
    fig,ax=plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax=sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int),
                annot=True)
    st.pyplot(fig)


    st.title("Most successful Athletes")
    sport_list=df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport=st.selectbox('Select a Sport ',sport_list)
    x=helper.most_successful(df,selected_sport)
    st.table(x)
if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')

    # Create sorted country list from the 'region' column
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    # Country selection dropdown
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    # ------------------ Year-wise Medal Tally ------------------
    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} Medals Tally over the Years")

    if country_df.empty:
        st.warning(f"No athlete able to win a medal for {selected_country}.")
    else:
        fig = px.line(country_df, x='Year', y='Medal', title='Medals Over Time')
        st.plotly_chart(fig)

    # ------------------ Sport-wise Heatmap ------------------
    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)

    if pt.empty:
        st.warning(f"No athlete able to win a medal for {selected_country}.")
    else:
        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(pt, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
        st.pyplot(fig)

    # ------------------ Top 10 Athletes ------------------
    top10_df,count = helper.most_successful_country(df, selected_country,count=10)
    if top10_df.empty:
        st.title(f"Top 10 Athletes of {selected_country}")
        st.warning(f"No athlete able to win a medal for {selected_country}.")
    else:
        if count==1:
            st.title(f"There is only {count} athlete from {selected_country} who won a medal")
            st.table(top10_df)
        elif 2<=count<10:
            st.title(f"There are only {count} athletes from {selected_country} who won a medal")
            st.table(top10_df)
        else:
            st.title(f"Top 10 Athletes of {selected_country}")
            st.table(top10_df)


if user_menu=='Athlete-wise Analysis':
    st.title('Men vs Female Participation Over the Years')
    final=helper.men_vs_female(df)
    fig=px.line(final,x='Year',y=['Male','Female'])
    fig.update_layout(autosize=False,width=1000,height=600)
    st.plotly_chart(fig)

    st.title('Men vs Female Total Participation ')
    fig, ax = plt.subplots()
    ax.bar(['Male','Female'], helper.men_vs_female_total(df),color=['skyblue', 'lightpink'])
    ax.set_ylabel('Number of Athletes')

    # Show in Streamlit
    st.pyplot(fig)

if user_menu=='Predictions':
    st.title('Predict how many Medals A country will win')

    year=['none',2028,2032,2036]
    country = helper.country_year_list_prediction(df)

    # Sport list
    sport_list = df['Sport'].dropna().unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'none')

    selected_year = st.selectbox("Select Year", year)
    selected_country = st.selectbox("Select Country", country)
    selected_sport = st.selectbox("Select Sport", sport_list)

    if st.button('Submit'):

        if selected_year == 'none' and selected_country == 'none' and selected_sport == 'none':
            st.warning("⚠️ Please fill all fields.")

        elif selected_year == 'none':
            st.warning("⚠️ Please fill the field: Year")

        elif selected_country == 'none':
            st.warning("⚠️ Please fill the field: Country")

        elif selected_sport == 'none':
            st.warning("⚠️ Please fill the field: Sport")

        else:
            # pass sport also
            x = prediction(df, selected_country, selected_year, selected_sport)

            if x is None:
                st.error(f"🎯 No prediction available for {selected_country} in {selected_sport} ({selected_year}) Olympics.")

            else:
                st.success(
                    f"🎯 {selected_country} is predicted to win {x['Total']} medals in {selected_sport} during {selected_year} Olympics."
                )

                st.markdown(f"""
                - 🥇 **Gold**: {x['Gold']}
                - 🥈 **Silver**: {x['Silver']}
                - 🥉 **Bronze**: {x['Bronze']}
                """)
                """)
