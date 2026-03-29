import asyncio
from graphics import *
from deux_mille_quarante_huit_game import Grille

class Jeu2048:
    """Classe représentant le jeu 2048 avec gestion de l'affichage et des actions utilisateur."""

    def __init__(self):
        """Initialise les paramètres du jeu et la fenêtre d'affichage."""
        self.cote_cases = 100
        self.nombre_de_cases = 4
        self.taille_fenetre = self.cote_cases * self.nombre_de_cases
        self.hauteur_score = 100  # Espace réservé pour le score
        self.couleur_fond = obtenir_couleur(240, 240, 240)
        self.couleur_fond_score = blanc

        # Palette de couleurs en teintes de violet
        self.couleurs_cases = {
            2: obtenir_couleur(235, 224, 255),
            4: obtenir_couleur(220, 200, 255),
            8: obtenir_couleur(200, 160, 255),
            16: obtenir_couleur(180, 130, 255),
            32: obtenir_couleur(160, 100, 255),
            64: obtenir_couleur(140, 70, 255),
            128: obtenir_couleur(120, 50, 255),
            256: obtenir_couleur(105, 30, 230),
            512: obtenir_couleur(90, 15, 200),
            1024: obtenir_couleur(80, 0, 170),
            2048: obtenir_couleur(70, 0, 140),
        }

        # Gestion des états de la grille pour les actions "Défaire" et "Refaire"
        self.etats_grille = []
        self.refaire_grille = []

        # Variables pour gérer les touches de défaire et refaire
        self.derniere_touche_defaire = None
        self.derniere_touche_refaire = None

        # Initialisation du jeu
        self.grille = Grille()
        self.init_affichage()
        self.afficher_grille()

    def init_affichage(self):
        """Initialisation de la fenêtre d'affichage."""
        init_fenetre(self.taille_fenetre, self.taille_fenetre + self.hauteur_score, "2048")
        remplir_fenetre(self.couleur_fond)

    def afficher_grille(self):
        """Affiche la grille et le score dans la fenêtre."""
        remplir_fenetre(self.couleur_fond)

        # Zone du score
        affiche_rectangle_plein((0, 0), (self.taille_fenetre, self.hauteur_score), self.couleur_fond_score)
        affiche_texte_centre(f"Score: {self.grille.score}", (self.taille_fenetre // 2, self.hauteur_score // 2), noir, 40)

        # Affichage des cases de la grille
        for i in range(self.nombre_de_cases):
            for j in range(self.nombre_de_cases):
                valeur = self.grille.grille[i][j]
                couleur = self.couleurs_cases.get(valeur, obtenir_couleur(60, 58, 50))

                affiche_rectangle_plein(
                    (j * self.cote_cases, (self.nombre_de_cases - 1 - i) * self.cote_cases + self.hauteur_score),
                    ((j + 1) * self.cote_cases, (self.nombre_de_cases - i) * self.cote_cases + self.hauteur_score),
                    couleur)

                if valeur != 0:
                    affiche_texte_centre(str(valeur),
                        ((j + 0.5) * self.cote_cases, (self.nombre_de_cases - 1 - i + 0.5) * self.cote_cases + self.hauteur_score),
                        noir if valeur <= 4 else blanc, 40)

        affiche_tout()

    async def afficher_game_over(self):
        """Affiche un message de fin de jeu."""
        affiche_texte_centre("Game Over!", (self.taille_fenetre // 2, self.taille_fenetre // 2 + self.hauteur_score), rouge, 60)
        affiche_tout()
        while pas_echap():
            await asyncio.sleep(0)  # Boucle asynchrone pour Pygbag

    def empiler(self, pile, element):
        """Empile un élément dans la pile."""
        pile.append(element)

    def depiler(self, pile):
        """Dépile un élément et le retourne."""
        return pile.pop() if pile else None

    async def jouer(self):
        """Boucle principale du jeu."""
        affiche_auto_off()

        while not self.grille.jeu_termine():
            fleche = get_fleches()

            # Sauvegarde de l'état avant mouvement
            if fleche in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                self.empiler(self.etats_grille, self.grille.cloner())
                self.refaire_grille.clear()

            # Déplacement de la grille
            if fleche == (-1, 0):
                await self.grille.deplacer('gauche')
            elif fleche == (1, 0):
                await self.grille.deplacer('droite')
            elif fleche == (0, 1):
                await self.grille.deplacer('haut')
            elif fleche == (0, -1):
                await self.grille.deplacer('bas')

            # Gestion de la touche "Défaire"
            if touche_enfoncee('K_BACKSPACE') and self.derniere_touche_defaire != 'K_BACKSPACE' and self.etats_grille:
                self.empiler(self.refaire_grille, self.grille.cloner())
                grille_clone = self.depiler(self.etats_grille)
                if grille_clone:
                    self.grille = grille_clone
                self.derniere_touche_defaire = 'K_BACKSPACE'

            # Gestion de la touche "Refaire"
            if touche_enfoncee('K_RETURN') and self.derniere_touche_refaire != 'K_RETURN' and self.refaire_grille:
                self.empiler(self.etats_grille, self.grille.cloner())
                grille_clone = self.depiler(self.refaire_grille)
                if grille_clone:
                    self.grille = grille_clone
                self.derniere_touche_refaire = 'K_RETURN'

            # Réinitialisation des touches "Défaire" et "Refaire" si elles sont relâchées
            if not touche_enfoncee('K_BACKSPACE'):
                self.derniere_touche_defaire = None
            if not touche_enfoncee('K_RETURN'):
                self.derniere_touche_refaire = None

            # Affichage de la grille mise à jour
            self.afficher_grille()
            affiche_tout()
            await asyncio.sleep(0)  # Permet au navigateur web de ne pas freeze (Pygbag)

        # Affichage du message "Game Over"
        await self.afficher_game_over()


async def run_game():
    jeu = Jeu2048()
    await jeu.jouer()

if __name__ == '__main__':
    asyncio.run(run_game())
