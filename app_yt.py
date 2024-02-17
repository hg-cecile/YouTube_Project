#### BOOTSTRAP
    
from flask import Flask, redirect, url_for, render_template, request, make_response

import plotly.express as px
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.io as pio
import copy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
from datetime import date, timedelta
import matplotlib.pyplot as plt

with open("./youtube-trending-video-dataset/FR_category_id.json", "r") as fichier:
    category = json.load(fichier)

df = pd.read_csv("./youtube-trending-video-dataset/FR_youtube_trending_data.csv", sep=",")
df["categoryId"] = df["categoryId"].astype(str)
# Création d'un dictionnaire pour mapper les ID aux titres
id_to_title_mapping = {item['id']: item['snippet']['title'] for item in category['items']}

# Création de la nouvelle colonne 'title'
df['categoryType'] = df['categoryId'].map(id_to_title_mapping)
df['publishedAt'] = df['publishedAt'].str.split('T').str[0]
df['trending_date'] = df['trending_date'].str.split('T').str[0]
df['publishedAt'] = pd.to_datetime(df['publishedAt'])
df['trending_date'] = pd.to_datetime(df['trending_date'])
df['publishedYear'] = df['publishedAt'].dt.year
df['nombre_videos']=1


df_inter = df[["categoryType", "view_count", "publishedYear","comment_count"]].groupby(["categoryType", "publishedYear"],                                                                        as_index=False).sum()
df_count = df.groupby('publishedYear',as_index=False)['categoryType'].value_counts()
df_count.rename(columns={"count":"video_count"}, inplace=True)
df_groupby = df_inter.merge(df_count, on = ["publishedYear","categoryType"])

df_lastest = copy.deepcopy(df)
df_lastest.sort_values(by=["title","trending_date"], ascending=[False, False], inplace=True)
df_lastest.drop_duplicates(subset=["title"],keep="first", inplace=True)
df_lastest.sort_values(by="view_count",ascending=False)

# mois = '2020-08'
def trend_youtuber_by_month(mois,categorie):
    temp_df =df[(df['trending_date'].dt.strftime('%Y-%m') == mois)&(df['categoryType']==categorie)].groupby(by=['channelTitle'])[['view_count','nombre_videos']].sum().reset_index().sort_values(ascending=False, by='view_count')
    temp_df = temp_df.merge(df[['channelTitle','channelId']].drop_duplicates(),on='channelTitle')
    temp_df.drop_duplicates(subset='channelTitle',inplace=True)
    temp_df.index += 1
    temp_df.insert(0, 'Classement', temp_df.index)
    return temp_df



def moteur_recherche(query : str, df : pd.DataFrame) -> pd.DataFrame : 
    """
    query : question à poser, requête du moteur de recherche
    df : prendre le df avec la ligne la plus récente
    """
    documents = list(set(df["title"].tolist()))

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    query_vector = tfidf_vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix)

    sorted_indices = similarities.argsort()[0][::-1]
    doc_results = []

    for index in sorted_indices:
        print(f"Similarity: {similarities[0][index]}, Document: {documents[index]}")
        if similarities[0][index]>0:
            doc_results.append(documents[index])

    df_results = df[df["title"].isin(doc_results[:20])]

    return df_results.sort_values(by="view_count",ascending=False)[:12]


def trend_of_the_day(categorie):
    data = df[(df["trending_date"] == date.today()) & (df["categoryType"] == categorie)]
    if data.shape[0] == 0 :
        data = df[(df["trending_date"] == (date.today() - timedelta(days=1)).strftime("%d-%m-%Y")) & (df["categoryType"] == categorie)]
    # data = data.sort_values(by="view_count",ascending=False)
    return data


app = Flask(__name__)


@app.route("/", methods=["GET","POST"])
def home():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        df_results = moteur_recherche(search_query, df_lastest)
        print("seach_query :", search_query)
        print("df_results : ", df_results)
        # Initialiser une liste pour stocker les informations de chaque ligne
        video_info_list = []

        # Itérer sur les trois premières lignes du DataFrame filtré
        for index, row in df_results.iterrows():
            title = row['title']
            thumbnail_url = row['thumbnail_link']
            video_id = row['video_id']
            channel_title = row['channelTitle']
            view_count = row['view_count']

            # Ajouter les informations à la liste
            video_info_list.append({
                'title': title,
                'thumbnail_url': thumbnail_url,
                'video_id': video_id,
                'channel_title': channel_title,
                'view_count': view_count
                    })
        # print("video_info_list", video_info_list)
        return render_template("base.html", df_results=df_results, video_info_list=video_info_list)
    else:
        return render_template("base.html")


@app.route("/music", methods=['GET', 'POST'])
def music():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_music = df[df["categoryType"] == "Music"].sort_values(by="view_count", ascending=False)
    df_music = df_music.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_music
        else:
            selected_year = int(selected_year)
            df_filtered = df_music[df_music['publishedYear'] == selected_year]
    else:
        df_filtered = df_music

    video_info_list = []

    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Music"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Music"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Music"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Music")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Music")

    return render_template("music.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)


@app.route("/sports", methods=['GET', 'POST'])
def sports():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Sports"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Sports"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Sports"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Sports"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Sports")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Sports")

    return render_template("sports.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)



@app.route("/entertainment", methods=['GET', 'POST'])
def entertainment():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Entertainment"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Entertainment"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Entertainment"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Entertainment"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Entertainment")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Entertainment")

    return render_template("entertainment.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)

@app.route("/comedy", methods=['GET', 'POST'])
def comedy():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Comedy"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Comedy"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Comedy"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Comedy"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Comedy")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Comedy")

    return render_template("comedy.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)


@app.route("/education", methods=['GET', 'POST'])
def education():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Education"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Education"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Education"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Education"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Education")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Education")

    return render_template("education.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)

@app.route("/gaming", methods=['GET', 'POST'])
def gaming():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Gaming"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Gaming"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Gaming"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Gaming"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Gaming")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Gaming")

    return render_template("gaming.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)

@app.route("/people_blog", methods=['GET', 'POST'])
def people_blog():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "People & Blogs"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "People & Blogs"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "People & Blogs"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "People & Blogs"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "People & Blogs")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "People & Blogs")

    return render_template("people_blog.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)

@app.route("/travel", methods=['GET', 'POST'])
def travel():
    liste_date = list(df['trending_date'].dt.strftime('%Y-%m').unique())
    df_temp = df[df["categoryType"] == "Travel & Events"].sort_values(by="view_count", ascending=False)
    df_temp = df_temp.drop_duplicates(subset=["channelId"], keep="first")
    if request.method == 'POST':
        selected_year = request.form.get('year')
        print(f"selected_year : {selected_year}")
        if selected_year == None :
            selected_year = 'all'
        if selected_year == 'all':
            df_filtered = df_temp
        else:
            selected_year = int(selected_year)
            df_filtered = df_temp[df_temp['publishedYear'] == selected_year]
    else:
        df_filtered = df_temp

    video_info_list = []
    for index, row in df_filtered.head(3).iterrows():
        title = row['title']
        thumbnail_url = row['thumbnail_link']
        video_id = row['video_id']
        channel_title = row['channelTitle']
        view_count = row['view_count']

        video_info_list.append({
            'title': title,
            'thumbnail_url': thumbnail_url,
            'video_id': video_id,
            'channel_title': channel_title,
            'view_count': view_count,
        })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"], 
               y=df_groupby[df_groupby["categoryType"] == "Travel & Events"]["view_count"],
                name="Nombre de vues"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Travel & Events"]["comment_count"],
                name="Nombre de commentaires"))
    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Travel & Events"]["video_count"],
                name="Nombre de vidéos",
                ))
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Statistiques globales",
                        method="update",
                        args=[{"visible": [True, True, True]},
                            {"title": "Statistiques globales",
                                "annotations": []}]),
                    dict(label="Nombre de vues",
                        method="update",
                        args=[{"visible": [True, False, False]},
                            {"title": "Nombre de vues",
                                "annotations": []}]),
                    dict(label="Nombre de commentaires",
                        method="update",
                        args=[{"visible": [False, True, False]},
                            {"title": "Nombre de commentaires",
                                "annotations": []}]),
                    dict(label="Nombre de vidéos",
                        method="update",
                        args=[{"visible": [False, False, True]},
                            {"title": "Nombre de vidéos",
                                "annotations": []}])
                ]),
            )
        ])
    fig.update_layout(title_text="STATISTIQUES")
    plot_html = pio.to_html(fig, full_html=False)

    tableau_data = trend_youtuber_by_month("2020-08", "Travel & Events")

    if request.method == 'POST':
        date_ = request.form.get('date')
        tableau_data = trend_youtuber_by_month(date_, "Travel & Events")

    return render_template("travel.html", 
                           plot_html=plot_html, 
                           video_info_list=video_info_list, 
                           tableau_data=tableau_data,
                           liste_date=liste_date)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5150)