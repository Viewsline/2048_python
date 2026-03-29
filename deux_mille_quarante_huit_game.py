import random
import asyncio

class Grille:
    def __init__(self, taille=4):
        """
        Initialise le plateau du jeu. Par défaut, la taille du plateau est 4x4.
        Le plateau est une liste 2D remplie de zéros, représentant des cases vides.
        """
        self.taille = taille  # Taille du plateau (par défaut 4x4)
        self.grille = [[0] * taille for _ in range(taille)]  # Crée un plateau 2D rempli de 0
        self.score = 0  # Initialisation du score à 0
        self.historique = []  # Liste pour stocker les états passés du plateau pour annulation (retour en arrière)
        self.ajouter_case()  # Ajoute une première case avec une valeur
        self.ajouter_case()  # Ajoute une deuxième case

    def ajouter_case(self):
        """
        Ajoute une nouvelle case avec la valeur 2 ou 4 dans une case vide choisie aléatoirement.
        """
        cases_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == 0]
        if cases_vides:  # S'il reste des cases vides
            i, j = random.choice(cases_vides)  # Choisit une case vide aléatoirement
            self.grille[i][j] = random.choice([2, 4])  # Assigne une valeur 2 ou 4

    def cloner(self):
        """
        Crée une copie de la grille actuelle, avec le même état et score.
        """
        copie = Grille(self.taille)  # Crée une nouvelle instance de Grille
        copie.grille = [ligne[:] for ligne in self.grille]  # Copie chaque ligne de la grille actuelle
        copie.score = self.score  # Copie le score
        return copie  # Retourne la copie du plateau

    def sauvegarder(self):
        """
        Sauvegarde l'état actuel de la grille et du score dans l'historique.
        Cela permet de faire un retour en arrière (annuler un mouvement).
        """
        self.historique.append((self.score, [ligne[:] for ligne in self.grille]))  # Sauvegarde de l'état actuel

    def dépiler(self):
        """
        Annule le dernier mouvement en revenant à l'état précédent de la grille.
        """
        if self.historique:  # Si l'historique contient des mouvements précédents
            self.score, self.grille = self.historique.pop()  # Récupère l'état précédent de la grille et du score

    async def deplacer(self, direction):
        """
        Effectue un mouvement dans une direction donnée (gauche, droite, haut, bas).
        Cela modifie le plateau et met à jour le score.
        """
        plateau_avant = [ligne[:] for ligne in self.grille]  # Sauvegarde l'état actuel du plateau avant le déplacement

        if direction == 'gauche':  # Déplacement vers la gauche
            for i in range(self.taille):
                self.grille[i] = self.fusionner_gauche(self.grille[i])  # Fusionne les cases de chaque ligne vers la gauche
        elif direction == 'droite':  # Déplacement vers la droite
            for i in range(self.taille):
                self.grille[i] = self.fusionner_gauche(self.grille[i][::-1])[::-1]  # Fusionne les cases de chaque ligne vers la droite
        elif direction == 'haut':  # Déplacement vers le haut
            for j in range(self.taille):
                colonne = [self.grille[i][j] for i in range(self.taille)]  # Récupère la colonne j
                colonne = self.fusionner_gauche(colonne)  # Fusionne la colonne vers le haut
                for i in range(self.taille):
                    self.grille[i][j] = colonne[i]  # Remplace la colonne j dans la grille
        elif direction == 'bas':  # Déplacement vers le bas
            for j in range(self.taille):
                colonne = [self.grille[i][j] for i in range(self.taille)]  # Récupère la colonne j
                colonne = self.fusionner_gauche(colonne[::-1])[::-1]  # Fusionne la colonne vers le bas
                for i in range(self.taille):
                    self.grille[i][j] = colonne[i]  # Remplace la colonne j dans la grille

        if self.grille != plateau_avant:  # Si le plateau a changé après le mouvement
            self.sauvegarder()  # Sauvegarde l'état actuel
            await asyncio.sleep(0.2)  # Attend un peu avant d'ajouter une nouvelle case (modifié pour l'asynchrone)
            self.ajouter_case()  # Ajoute une nouvelle case vide

    def fusionner_gauche(self, ligne):
        """
        Fusionne les cases d'une ligne vers la gauche. Les cases de même valeur fusionnent.
        Exemple : [2, 2, 0, 4] -> [4, 4, 0, 0]
        """
        nouvelle_ligne = [i for i in ligne if i != 0]  # Supprime les zéros pour ne garder que les valeurs
        fusion_effectuee = [False] * len(nouvelle_ligne)  # Liste pour marquer les cases fusionnées

        for i in range(len(nouvelle_ligne) - 1):  # Parcours chaque case de la ligne
            if nouvelle_ligne[i] == nouvelle_ligne[i + 1] and not fusion_effectuee[i] and not fusion_effectuee[i + 1]:
                nouvelle_ligne[i] *= 2  # Fusionne les deux cases en doublant la valeur
                self.score += nouvelle_ligne[i]  # Ajoute la valeur fusionnée au score
                nouvelle_ligne[i + 1] = 0  # Réinitialise la case fusionnée à 0
                fusion_effectuee[i] = True  # Marque la case comme ayant été fusionnée

        nouvelle_ligne = [i for i in nouvelle_ligne if i != 0]  # Supprime les zéros laissés par les fusions
        return nouvelle_ligne + [0] * (self.taille - len(nouvelle_ligne))  # Complète la ligne avec des zéros pour la rendre de taille égale

    def mouvements_possibles(self):
        """
        Vérifie s'il y a encore des mouvements possibles sur le plateau.
        Cela inclut les fusions possibles ou les cases vides où une nouvelle case peut être placée.
        """
        for i in range(self.taille):
            for j in range(self.taille - 1):
                if self.grille[i][j] == self.grille[i][j + 1] or self.grille[j][i] == self.grille[j + 1][i]:
                    return True  # Si une fusion est possible entre deux cases voisines
        return any(0 in ligne for ligne in self.grille)  # Ou s'il existe une case vide

    def jeu_termine(self):
        """
        Vérifie si le jeu est terminé, c'est-à-dire s'il n'y a plus de mouvements possibles.
        """
        return not self.mouvements_possibles()  # Le jeu est terminé si aucun mouvement n'est possible
