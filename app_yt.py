#### BOOTSTRAP

from flask import Flask, redirect, url_for, render_template, request

import plotly.express as px
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.io as pio
import copy

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

df_inter = df[["categoryType", "view_count", "publishedYear","comment_count"]].groupby(["categoryType", "publishedYear"],                                                                        as_index=False).sum()
df_count = df.groupby('publishedYear',as_index=False)['categoryType'].value_counts()
df_count.rename(columns={"count":"video_count"}, inplace=True)
df_groupby = df_inter.merge(df_count, on = ["publishedYear","categoryType"])

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/home_page")
def home_page():
    return render_template("base_extend.html")

@app.route("/music", methods=['GET', 'POST'])
def music():
    df_music = df[df["categoryType"] == "Music"].sort_values(by="view_count", ascending=False)
    df_music = df_music.drop_duplicates(subset=["channelId"], keep="first")

    if request.method == 'POST':
        selected_year = request.form.get('year')

        if selected_year == 'all':
            df_filtered = df_music
        else:
            selected_year = int(selected_year)
            df_filtered = df_music[df_music['publishedYear'] == selected_year]
    else:
        # Traitement lorsque le formulaire n'est pas soumis
        df_filtered = df_music

    # Initialiser une liste pour stocker les informations de chaque ligne
    video_info_list = []

    # Itérer sur les trois premières lignes du DataFrame filtré
    for index, row in df_filtered.head(3).iterrows():
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

    # Initialize figure
    fig = go.Figure()

    # Add Traces

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Music"]["view_count"],
                name="Nombre de vues",
                ))

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Music"]["comment_count"],
                name="Nombre de commentaires",
                ))

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

    # Set title
    fig.update_layout(title_text="Titre à changer")

    # Utiliser plotly.io.to_html pour convertir la figure en HTML
    plot_html = pio.to_html(fig, full_html=False)

    return render_template("music.html", plot_html=plot_html, video_info_list=video_info_list)



@app.route("/sports", methods=['GET', 'POST'])
def sports():
    df_sport = df[df["categoryType"] == "Sports"].sort_values(by="view_count", ascending=False)
    df_sport = df_sport.drop_duplicates(subset=["channelId"], keep="first")

    if request.method == 'POST':
        selected_year = request.form.get('year')

        if selected_year == 'all':
            df_filtered = df_sport
        else:
            selected_year = int(selected_year)
            df_filtered = df_sport[df_sport['publishedYear'] == selected_year]
    else:
        # Traitement lorsque le formulaire n'est pas soumis
        df_filtered = df_sport

    # Initialiser une liste pour stocker les informations de chaque ligne
    video_info_list = []

    # Itérer sur les trois premières lignes du DataFrame filtré
    for index, row in df_filtered.head(3).iterrows():
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

    # Initialize figure
    fig = go.Figure()

    # Add Traces

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Sports"]["view_count"],
                name="Nombre de vues",
                ))

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Sports"]["comment_count"],
                name="Nombre de commentaires",
                ))

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

    # Set title
    fig.update_layout(title_text="Titre à changer")

    # Utiliser plotly.io.to_html pour convertir la figure en HTML
    plot_html = pio.to_html(fig, full_html=False)

    return render_template("sports.html", plot_html=plot_html, video_info_list=video_info_list)



@app.route("/entertainment", methods=['GET', 'POST'])
def entertainment():
    df_entertainment = df[df["categoryType"] == "Entertainment"].sort_values(by="view_count", ascending=False)
    df_entertainment = df_entertainment.drop_duplicates(subset=["channelId"], keep="first")

    if request.method == 'POST':
        selected_year = request.form.get('year')

        if selected_year == 'all':
            df_filtered = df_entertainment
        else:
            selected_year = int(selected_year)
            df_filtered = df_entertainment[df_entertainment['publishedYear'] == selected_year]
    else:
        # Traitement lorsque le formulaire n'est pas soumis
        df_filtered = df_entertainment

    # Initialiser une liste pour stocker les informations de chaque ligne
    video_info_list = []

    # Itérer sur les trois premières lignes du DataFrame filtré
    for index, row in df_filtered.head(3).iterrows():
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

    # Initialize figure
    fig = go.Figure()

    # Add Traces

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Entertainment"]["view_count"],
                name="Nombre de vues",
                ))

    fig.add_trace(
        go.Bar(x=df_groupby["publishedYear"],
                y=df_groupby[df_groupby["categoryType"] == "Entertainment"]["comment_count"],
                name="Nombre de commentaires",
                ))

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

    # Set title
    fig.update_layout(title_text="Titre à changer")

    # Utiliser plotly.io.to_html pour convertir la figure en HTML
    plot_html = pio.to_html(fig, full_html=False)

    return render_template("entertainment.html", plot_html=plot_html, video_info_list=video_info_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5150)
