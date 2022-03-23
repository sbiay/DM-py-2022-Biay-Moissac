La librairie de Moissac
===

![Paris-BNF-Lat-2077-f32v](app/static/img/btv1b105254751_f72.jpg)

*La librairie de Moissac* est une application Python-Flask qui permet la consultation et l'enrichissement d'une base de données des manuscrits attestés dans la *librairie* (c'est-à-dire la bibliothèque) de l'abbaye Saint-Pierre de Moissac tout au long du Moyen Âge. 

# Présentation générale
## L'histoire
Puissante abbaye bénédictine fondée au VIIe siècle, l'abbaye de Moissac devint au XIe siècle un centre de production de manuscrits très actif ainsi que le donataire de nombreux autres *codices*, provenant en particulier de l'abbaye de Cluny. Ses livres firent la délectation des collectionneurs à partir du XVIe siècle, tout particulièrement de Jean-Baptiste Colbert. Versée dans les collections de la Bibliothèque du Roi en 1732, la collection Colbert conduisit *in fine* de nombreux manuscrits faits ou possédés par l'abbaye de Moissac au sein des collections de la Bibliothèque nationale de France.

## Les sources des données
Cette application propose les notices d'une petite partie de ces *codices*. Pour chacun d'entre-eux, nous avons récolté les informations ayant trait à leur histoire et à leur contenu dans deux sources :
- Les notices de ces *codices* publiées sur les sites des institutions qui les conservent, en particulier le site de la Bibliothèque nationale de France [Archives et manuscrits](https://archivesetmanuscrits.bnf.fr) ;
- Le catalogue établi par Jean Dufour pour sa thèse d'École des chartes en 1963 :
    - La position de cette thèse est accessible sur le site [Thenc@ : Thèses ENC accessibles en ligne](https://bibnum.chartes.psl.eu/s/thenca/item/56764#?c=&m=&s=&cv=&xywh=-2%2C-1%2C4%2C1) ;
    - L'ouvrage a été remanié et publié par la suite : *La bibliothèque et le scriptorium de Moissac*, Genève, Droz, 1972.


# Installation
Téléchargez l'archive zip de l'application, disponible sur cette page via le bouton **Code**, puis dézippez-la dans le dossier de votre choix.

## Sous Windows
L'installation de Python 3 est nécessaire pour utiliser cette application. Nous recommandons la distribution [Anaconda](https://www.anaconda.com/products/individual).

Une fois la distribution Anaconda installée :
- Lancez depuis le menu Démarrer l'**Anaconda Powershell Prompt** ;
- Déplacez-vous dans le dossier de l'application dézippée ;
- Créez un environnement virtuel à l'aide de la commande :
    ```shell
    $ python3 -m venv env
    ```
- Activez cet environnement virtuel à l'aide de la commande (opération à **réitérer** à chaque lancement de l'application) :
    ```shell
    $ source env/bin/activate
    ```
- Installer les modules requis grâce à la commande :
    ```shell
    $ pip install -r requirements.txt
    ```
- Lancez l'application grâce à la commande :
    ```shell
    python3 run.py
    ```
- Vous devriez pouvoir ouvrir l'application dans un navigateur web grâce à [ce lien](http://127.0.0.1:5000/).

## Sous Linux (Ubuntu/Debian)
- Pour installer Python 3, ouvrez un terminal et saisissez la commande :
    ```shell
    $ sudo apt-get install python3 libfreetype6-dev python3-pip python3-virtualenv
    ```
- Déplacez-vous dans le dossier de l'application dézippé.
- Créez un environnement virtuel à l'aide de la commande :
    ```shell
    $ python3 -m venv env
    ```
- Activez cet environnement virtuel à l'aide de la commande (opération à **réitérer** à chaque lancement de l'application) :
    ```shell
    $ source env/bin/activate
    ```
- Installer les modules requis grâce à la commande :
    ```shell
    $ pip install -r requirements.txt
    ```
- Lancez l'application grâce à la commande :
    ```shell
    python3 run.py
    ```
- Vous devriez pouvoir ouvrir l'application dans un navigateur web grâce à [ce lien](http://127.0.0.1:5000/).

# Sélection des données et choix de modélisation
Tout en récoltant les descriptions à caractère historique et matériel proposées par les notices du site [Archives et manuscrits](https://archivesetmanuscrits.bnf.fr) ainsi que certaines informations à caractère paléographique (plutôt issue de l'ouvrage de J. Dufour), nous avons modélisé dans notre base de données les informations suivantes :
- La plus grande attention a été accordée aux **oeuvres** contenues dans les *codices* avec leur **auteur** ;
- Nous avons également modélisé l'**origine** de ces *codices*, c'est-à-dire le lieu (ou les lieux hypothétiques) où ils ont été fabriqués (qui n'est pas toujours Moissac) ;
- Ainsi que les lieux de **provenances** de ces manuscrits, c'est-à-dire les lieux autres que Moissac (dénominateur commun de notre collection) où ils ont été conservés au Moyen Âge ou à l'époque moderne (notamment les collections comme celle de Colbert).

## Modèle conceptuel
![modele-conceptuel](./app/db/mcd.svg)

## Les unités codicologiques
Nous avons opté pour un modèle conceptuel qui distingue les *codices* des **unités codicologiques** qui les composent. La plupart des *codices* sont d'un seul tenant : ils ne contiennent donc qu'une seule unité codicologique. 

D'autres sont de nature composite, en particulier **Paris, BnF, Latin 2077**. Les oeuvres contenues ont donc été associées à chacune de ces unités plutôt qu'au *codex* en général, et ce afin d'en respecter la chronologie propre.

# Fonctionnalités
## Recherche
L'application propose deux modalités de recherche dans la base de données : simple et avancée.

### Recherche simple
La recherche simple est inclusive par défaut et ne retourne que des *codices* : elle retourne par conséquent tous les *codices* pertinents par rapport à chacun des mots-clés de la saisie. L'opérateur "ET" peut être saisi avec les mots-clés, ce qui rend la recherche exclusive : elle ne renvoie dès lors que les *codices* pertinents par rapport à tous les mots-clés saisis.

Afin de bénéficier des multiples formes de titres d'oeuvre et de noms d'auteurs décrits sur data.bnf.fr, cette recherche croise les identifiants ark d'auteurs et d'oeuvres contenus dans la base de données avec les ark répondant aux mêmes mots-clés interrogés sur data.bnf.fr. Il est donc possible de trouver les *codices* associés à l'auteur "Augustin (saint, 354-430)" en employant les mots-clés "augustinus hipponensis" par exemple. Il en va de même pour les titres d'oeuvres.

### Recherche avancée
De même que la recherche simple, toutes les formes de noms d'auteurs ou de titres d'oeuvres existant sur data.bnf.fr sont moissonnés par la recherche avancée et croisés avec les données de la base locale.

La recherche avancée est à la fois exclusive et inclusive : 
- Elle ne renvoie que les *codices* pertinents par rapport à tous les mots-clés saisis ;
- Elle renvoie toutes les oeuvres répondant à tous les mots-clés saisis dans le champ dédié (indépendamment des mots-clés saisis dans le champ "auteurs") ;
- Elle renvoie tous les auteurs répondant à tous les mots-clés saisis dans le champ dédié (indépendamment des mots-clés saisis dans le champ "oeuvres") ;

Enfin, l'opérateur "OU" peut être saisi avec les mots-clés dans les champs "oeuvre" et "auteur", ce qui rend la recherche inclusive pour ces types de données respectifs.

Prenons pour exemple une recherche portant sur les mots-clés suivants :
- Auteur : "Augustin OU Grégoire"
- Oeuvre : "corpore"

Elle retournera :
- En auteurs : saint Augustin et Grégoire le Grand ;
- En oeuvres : *De corpore et sanguine Domini*, Paschase Radbert (saint) ;
- En codex : Paris, BNF, Latin 2077, car il contient à la fois des oeuvres d'Augustin, d'autres de Grégoire, et le *De corpore et sanguine Domini*, Paschase Radbert.

Une recherche portant sur les mots-clés suivants :
- Auteur : "Augustin Grégoire"
- Oeuvre : "corpore"

retournera :
- En auteurs : rien, car aucun auteur ne contient Augustin et Grégoire dans son nom ;
- En oeuvres : *De corpore et sanguine Domini*, Paschase Radbert (saint) ;
- En codex : Paris, BNF, Latin 2077 et Leiden, Universiteitsbibliotheek, BPL 1822 car ils contiennent tous les deux le *De corpore et sanguine Domini*, Paschase Radbert.

Une recherche portant sur les mots-clés suivants :
- Auteur : "Augustin OU Grégoire"
- Oeuvre : "Apologeticum"

retournera :
- En auteurs : saint Augustin et Grégoire le Grand ;
- En oeuvres : *Apologeticum*, Tertullien.
- En codex : aucun, car aucun *codex* ne contient à la fois des oeuvres d'Augustin, d'autres de Grégoire et l'*Apologeticum* de Tertullien.

Enfin, une recherche portant sur le seul mot-clé suivant :
- Auteur : "saint"

retournera une longue liste d'auteur, mais aucun *codex*, car aucun *codex* ne réunit des oeuvres de chacun des auteurs de la liste retournée.

## Création de contenus
Dans la mesure où les objets principaux de la base de données sont les *codices*, la création d'une oeuvre est strictement conditionnée à son rattachement à une unité codicologique déterminée : elle ne peut se faire que par le formulaire de mise à jour d'un codex, au niveau d'une unité codicologique particulière.

Pour les oeuvres qui ne sont pas anonymes, elles ne peuvent être créées qu'une fois leur auteur créé.

Cette démarche a été développée avec de manière contraignante : seuls les auteurs et les oeuvres présents sur le site data.bnf.fr peuvent être sélectionnées. Leur récupération est opérée au moyen de requêtes sparql adressées au sparql *endpoint* de data.bnf.fr. L'idée est de contraindre l'utilisateur à prévilégier des données liées avant de lui donner la possibilité (non encore développée dans l'application), de créer des contenus *ad hoc*.

Ce privilège accordé aux données liées apporte de l'eau au moulin des fonctionnalités de recherche de l'application, exposée ci-dessus.


# Développements possibles
## Création et mise à jour
- Il n'est pas possible de créer de nouvelles unités codicologiques ;
- Il n'est pas possible de créer des auteurs et des oeuvres absents de Data-BNF ;
- Proposer un filtre de recherche par date.