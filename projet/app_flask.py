from flask import Flask,render_template,request , redirect , url_for ,session 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///base.db'#configuration renseignements de l'url de notre base de donnes et on l'appel toto.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False# desactivation du la fonction de suivi des objets en memoire, car elle consomme de la memoire
db=SQLAlchemy(app)#creation d'une instance db

class Utilisateurs(db.Model):#creation d'une table dans la db model represente une table dans la db c'est une class, ici elle herite de sqlalchemy pour fontionner
    id= db.Column(db.Integer,primary_key=True)# numero unique de chaque utilisateur
    nom=db.Column(db.String(100),nullable=False)# nom de l'utilisateur
    email=db.Column(db.String(120),unique=True,nullable=False)#unique=true veut dire que deux utilisateurs ne peuvent pas avoir le meme email
    droit_admin=db.Column(db.Boolean, default=False)#champ administrateur
    mdp=db.Column(db.String(10),nullable=False)

    def __repr__(self):
            return f"Todo {self.nom}"#afficher l'utilisateur de maniere lisible dans la console
    
    

#fonction pour cree la db et ajouter des element
def init_base():
    with app.app_context():#contexte d'application pour savoir quelle application appeler
        db.create_all()
    #verification si il y a deja des taches
        if Utilisateurs.query.first() is None:
            t1 = Utilisateurs(nom="ODIA KALONJI AGOSTINHO", email="agostinhomelano@gmail.com",mdp="1234")
           # t2 = Utilisateur(nom="Faire un projet test")
            db.session.add_all([t1])#ajouter plusieurs objet d'u coup
            db.session.commit()#enregistrer les changements dans la db 
            print("Taches initiales ajoutees.")
        else:
            print("La base contient deja des donnes.")


app.secret_key="1a6676b463603eaa5118f0a289721f25d52b7fb7be2afebccfadaa455b618b7f"

@app.route("/")
def accueil():
    return render_template("acceuil.html")

@app.route("/admin")
def admin():#verification si l'utilisateur est connecte
    if 'utilisateur' not in session or session['utilisateur'] != 'Admin':
        return redirect('/connexion')

    utilisateur = Utilisateurs.query.filter_by(nom=session['utilisateur']).first()
    if utilisateur and utilisateur.droit_admin:
        utilisateurs = Utilisateurs.query.all()
        return render_template("admin.html", utilisateurs=utilisateurs)
    else:
        return "Accès refusé : vous n'êtes pas administrateur."



@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form['nom']
        email = request.form['email']
        mdp = request.form['mdp']
        #verifier si tout les champ son rempli
        if not nom or not email or not mdp :
            return "vous n'avez pas rempli tous les champs"

        # Vérifie si l'email existe déjà dans la base
        utilisateur_existant = Utilisateurs.query.filter_by(email=email).first()
        if utilisateur_existant:
            return "Cet email est déjà utilisé."

        # Crée un nouvel utilisateur
        hash_mdp= generate_password_hash(mdp)
        nouvel_utilisateur = Utilisateurs(nom=nom, email=email, mdp=mdp)
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        return redirect('/formations')

    return render_template("inscription.html")
# @app.route("/modification_mpd/<int:id>",methods=["POST"])
# def mod_mpd(id):
#     nouv_mdp=request.form["nouveau_mdp"]
#     utilisateurs= Utilisateurs.query.get(id)
#     if utilisateurs:
#         utilisateurs.mdp=nouv_mdp
#         db.session.commit()
#         return "mot de passe mis a jour avec succes"
#     else :
#         return "utilisateur non trouve"

        
@app.route("/connexion",methods=["POST","GET"])
def connexion():
    if request.method =="POST": #tester si la methode est post ou pas, on verifie si l'utilisateur a clique sur "connexion"
        #recuperation des donnee du formulaire html
        # nom = request.form['nom']
        email = request.form['email'] 
        mdp = request.form['mdp']
       #recherche dans la base de donnee
        utilisateur=Utilisateurs.query.filter_by(email=email).first()# first()prend le premier element trouver dans la db
        from werkzeug.security import check_password_hash
        if utilisateur and check_password_hash(utilisateur.mdp==mdp):#Si il existe on le connecte
            session['utilisateur']=utilisateur.nom# enregistre son nom dans la session
            return redirect('/formations')
        else:
            return "identifiant incorects"

    return render_template("connexion.html")

@app.route("/formations")
def formations():
    if 'utilisateur' not in session:
        return redirect('/connexion')
    return  render_template("formations.html")

@app.route("/produits")
def produits():
    return  render_template("produits.html")

@app.route("/reservation")
def reservation():
    return  render_template("reservation.html")

@app.route("/commander",methods=["GET","POST"])
def commandes():
    # if request.method=="POST":
    #     produit=request.form.get("produit")
    #     quantite=request.form.get("quantite")
    #     print(f"produit:{produit},Quantite:{quantite}")
    #     return render_template("confirmation.html",produit=produit,quantite=quantite)
    return  render_template("commandes.html")


@app.route("/actualites")
def actualites():
    return  render_template("actualites.html")

@app.route("/commentaires")
def commentiares():
    return render_template("commentaires.html")

# utilisateurs=[
#     {"nom":"odia","postnom":"kalonji","prenom":"agos","mdp":"1234"},
# ]
# def recherche_utilisateur(nom,postnom,prenom,mot_de_passe):
#     for utilisateur in utilisateurs:
#         if utilisateur['nom']==nom and utilisateur['mdp']==mot_de_passe and utilisateur['postnom']==postnom and utilisateur['prenom']==prenom  :
#             return utilisateur
#     return None


if __name__=='__main__':
    init_base()
    app.run(debug=True)