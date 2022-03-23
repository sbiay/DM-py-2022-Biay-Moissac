La librairie de Moissac
===

*La librairie de Moissac* est une application Python-Flask qui permet la consultation et l'enrichissement d'une base de données des manuscrits conservés dans la *librairie* (c'est-à-dire la bibliothèque) de l'abbaye Saint-Pierre de Moissac tout au long du Moyen Âge. 

# Présentation générale
## L'histoire
Puissante abbaye bénédictine fondée dès le VIIe siècle, l'abbaye de Moissac devint au XIe siècle un centre de production de manuscrits très actif ainsi que le donataire de nombreux autres *codices*, provenant en particulier de l'abbaye de Cluny. Ses collections firent la délectation des collectionneurs de livres anciens à partir du XVIe siècle, tout particulièrement Jean-Baptiste Colbert. Versée dans les collections de la Bibliothèque du Roi en 1732, la collection Colbert conduisit *in fine* de nombreux manuscrits faits ou possédés par l'abbaye de Moissac au sein des collections de la Bibliothèque nationale de France.

## Les sources des données
Cette application propose les notices d'une petite partie de ces *codices*. Pour chacun d'entre-eux nous avons récolté les informations ayant trait à leur histoire et à leur contenu dans deux sources :
- Les notices de ces *codices* publiées sur les sites des institutions qui les conservent, en particuliers le site de la Bibliothèque nationale de France [Archives et manuscrits](https://archivesetmanuscrits.bnf.fr) ;
- Le catalogue établi par Jean Dufour pour sa thèse d'École des chartes en 1963 :
    - La position de cette thèse est accessible sur le site [Thenc@ : Thèses ENC accessibles en ligne](https://bibnum.chartes.psl.eu/s/thenca/item/56764#?c=&m=&s=&cv=&xywh=-2%2C-1%2C4%2C1) ;
    - L'ouvrage a été remanié et publié par la suite : *La bibliothèque et le scriptorium de Moissac*, Genève, Droz, 1972.


# Installation
Téléchargez l'archive zip de l'application, disponible sur cette page via le bouton **Code**, puis dézippez-la dans le dossier de votre choix.

## Sous Windows
L'installation de Python 3 est nécessaire pour utiliser cette application. Nous recommandons la distribution [Anaconda](https://www.anaconda.com/products/individual).

Une fois la distribution Anaconda installée :
- Lancer depuis le menu Démarrer l'**Anaconda Powershell Prompt** ;
- Déplacez-vous dans le dossier de l'application dézippé.
- Créez un environnement virtuel à l'aide de la commande :
    ```shell
    $ python3 -m venv env
    ```
- Activez cet environnement virtuel à l'aide de la commande (opération à **réitérer** à chaque lancement de l'application) :
    ```shell
    $ source venv/bin/activate
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
Pour installer Python 3, ouvrez un terminal et saisissez la commande :
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
    $ source venv/bin/activate
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

# Fonctionnalités

# Sélection des données et choix de modélisation
Tout en récoltant les descriptions à caractère historique et matérielle proposées par les notices du site [Archives et manuscrits](https://archivesetmanuscrits.bnf.fr) ainsi que certaines informations à caractère paléographique (plutôt issue de l'ouvrage de J. Dufour), nous avons modélisé dans notre base de données les informations suivantes :
- La plus grande attention a été accordée aux **oeuvres** contenues dans les *codices* avec leur **auteur** ;
- Nous avons également modélisé l'**origine** de ces *codices*, c'est-à-dire le lieu (ou les lieux hypothétiques) où ils ont été fabriqués (qui n'est pas toujours Moissac) ;
- Ainsi que les lieux de **provenances** de ces manuscrits, c'est-à-dire les lieux autres que Moissac (dénominateur commun de notre collection) où ils ont été conservés au Moyen Âge ou à l'époque moderne (notamment les collections comme celle de Colbert).

## Les unités codicologiques
Nous avons opté pour un modèle conceptuel qui distingue les *codices* des **unités codicologiques** qui les composent. La plupart des *codices* sont d'un seul tenant ; d'autres sont de nature composite, en particulier **Paris, BnF, Latin 2077**. Les oeuvres contenues ont donc été associées à chacune de ces unités plutôt qu'au codex en général, et ce afin d'en respecter en particulier la chronologie propre.

# Développements possibles
## Création et mise à jour
- Il n'est pas possible de créer de nouvelles unités codicologiques ;
- Il n'est pas possible de créer des auteurs et des oeuvres absents de Data-BNF.