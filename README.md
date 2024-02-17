# YouStats : Elevate your stats, choose YouStats!

Dans le cadre du cours du cours de *Système d'exploitation: Linux* notre équipe a décidé de proposer une application pour créateur de contenu YouTube. Découvrez avec Cécile Huang, Yoan Jsem et Alice Liu, YouStats notre projet au combien populaire.

## Table des matières

* [A Propos du Projet](#a-propos-du-projet)
* [Ouvrir l'application](#ouvrir-l-application)
* [Organisation du Projet](#organisation-du-projet)
* [Contact](#contact)

## A Propos du Projet
YouStats est une application destinée aux créateurs de contenu, notamment les YouTubeurs. Déployée via Docker pour une expérience utilisateur uniforme, elle collecte les données depuis un dataset Kaggle mis à jour quotidiennement qui nous permet de suivre les tendances YouTube en temps réel. YouStats offre un Top 3 des vidéos tendances par année choisie et des graphiques détaillés sur les vues, commentaires et vidéos par catégorie et année en plus d'un moteur de recherche à tendance. Notre objectif est d'aider les créateurs de contenu à comprendre leur public, suivre les tendances et élargir leur audience, tout en offrant une expérience enrichissante aux spectateurs français.

<a name="a-propos-du-projet"></a>

## Ouvrir l'application
1. Cloner le repository
```
git clone https://github.com/Naoyy/YouTube_Project.git
cd YouTube_Project
```

2. Ajouter les credentials kaggle dans un dossier .env

```
mkdir .env
cd .env
[ Ajouter les credentials kaggle (kaggle.json)]
cd ..
```

3. Construire l'image à partir du Dockerfile puis ouvrir l'application
```
docker build -t youtubeapp:latest .
```
(vérifiez que vous vous situez bien là où se trouve le Dockerfile)

On lance ensuite l'application via docker sur le port **5150** qu'il faudra ouvrir au préalable !
```
docker run -it -p 5150:5150 youtubeapp:latest
```

Après avoir lancé cette commande il ne vous reste plus qu'à accéder au local host qui possède le port 5150.

Une fois cela fait il ne vous reste plus qu'à apprécier votre experience !
<a name="ouvrir-l-application"></a>

## Organisation de l'appli

Dans le cadre du projet nous requêtons les données kaggle provenant de [YouTube Trending Video Dataset(updated daily)](https://www.kaggle.com/datasets/rsrishav/youtube-trending-video-dataset). Plus particulièrement nous nous servons uniquement du dataset concernant les données françaises. Cette donnée est automatiquement récupérée via un script bash, on s'assure ensuite d'avoir les permissions nécessaires sur la donnée récoltée à l'aide de l'intégrateur. On finit par processer la donnée avant de construire l'application.

Dans le dossier data_collector on retrouve les scripts qui permettent de collecter la donnée depuis kaggle. Cette donnée est ensuite intégrée via le script se trouvant dans le dossier integrator, on s'assure que la donnée a bien été récoltée (existante) et qu'on puisse lire et écrire sur cette donnée. Ensuite on s'occupe de process la donnée, dans notre cas il s'agira uniquement de duppliquer cette donnée afin de pouvoir l'utiliser. 

Les dossier static/ et templates/ comportent les fichiers nécessaires pour construire le rendu visuel de la web app.

- data_collector/
    - another_collector.py
    - fait_auto.sh

- integrator/
    - working_y_n.sh

- processor/
    - process.sh

- static/
    - fond_vectoriel.jpg
    - style.css
    - youtube-logo-png-46031.png

- templates/
    - base.html
    - comedy.html
    - education.html
    - entertainment.html
    - gaming.html
    - music.html
    - people_blog.html
    - search_results.html
    - sports.html
    - travel.html

- .gitignore
- Dockerfile
- README.md
- app.py
- launch.sh
- requirements.txt

<a name="organisation-du-projet"></a>

## Contact

- [Cécile Huang](https://github.com/hg-cecile) - cecilehuang0@gmail.com
- [Yoan Jsem](https://github.com/Naoyy) - yoan.jsem@gmail.com
- [Alice Liu](https://github.com/alice-l1) - alice.liu015@gmail.com
<a name="contact"></a>