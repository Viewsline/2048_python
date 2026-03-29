# main.py — Point d'entrée Pygbag pour le jeu 2048
# Ce fichier utilise pygame directement (sans graphics.py) pour être compatible WebAssembly/Pygbag.

import asyncio
import pygame
import random

# ===================== LOGIQUE DU JEU (tirée de deux_mille_quarante_huit_game.py) =====================

class Grille:
    def __init__(self, taille=4):
        self.taille = taille
        self.grille = [[0] * taille for _ in range(taille)]
        self.score = 0
        self.historique = []
        self.ajouter_case()
        self.ajouter_case()

    def ajouter_case(self):
        cases_vides = [(i, j) for i in range(self.taille) for j in range(self.taille) if self.grille[i][j] == 0]
        if cases_vides:
            i, j = random.choice(cases_vides)
            self.grille[i][j] = random.choice([2, 4])

    def cloner(self):
        copie = Grille.__new__(Grille)
        copie.taille = self.taille
        copie.grille = [ligne[:] for ligne in self.grille]
        copie.score = self.score
        copie.historique = []
        return copie

    def sauvegarder(self):
        self.historique.append((self.score, [ligne[:] for ligne in self.grille]))

    def depiler(self):
        if self.historique:
            self.score, self.grille = self.historique.pop()

    def deplacer(self, direction):
        plateau_avant = [ligne[:] for ligne in self.grille]
        if direction == 'gauche':
            for i in range(self.taille):
                self.grille[i] = self.fusionner_gauche(self.grille[i])
        elif direction == 'droite':
            for i in range(self.taille):
                self.grille[i] = self.fusionner_gauche(self.grille[i][::-1])[::-1]
        elif direction == 'haut':
            for j in range(self.taille):
                colonne = [self.grille[i][j] for i in range(self.taille)]
                colonne = self.fusionner_gauche(colonne)
                for i in range(self.taille):
                    self.grille[i][j] = colonne[i]
        elif direction == 'bas':
            for j in range(self.taille):
                colonne = [self.grille[i][j] for i in range(self.taille)]
                colonne = self.fusionner_gauche(colonne[::-1])[::-1]
                for i in range(self.taille):
                    self.grille[i][j] = colonne[i]
        if self.grille != plateau_avant:
            self.sauvegarder()
            self.ajouter_case()

    def fusionner_gauche(self, ligne):
        nouvelle_ligne = [i for i in ligne if i != 0]
        fusion_effectuee = [False] * len(nouvelle_ligne)
        for i in range(len(nouvelle_ligne) - 1):
            if nouvelle_ligne[i] == nouvelle_ligne[i + 1] and not fusion_effectuee[i] and not fusion_effectuee[i + 1]:
                nouvelle_ligne[i] *= 2
                self.score += nouvelle_ligne[i]
                nouvelle_ligne[i + 1] = 0
                fusion_effectuee[i] = True
        nouvelle_ligne = [i for i in nouvelle_ligne if i != 0]
        return nouvelle_ligne + [0] * (self.taille - len(nouvelle_ligne))

    def mouvements_possibles(self):
        for i in range(self.taille):
            for j in range(self.taille - 1):
                if self.grille[i][j] == self.grille[i][j + 1] or self.grille[j][i] == self.grille[j + 1][i]:
                    return True
        return any(0 in ligne for ligne in self.grille)

    def jeu_termine(self):
        return not self.mouvements_possibles()


# ===================== AFFICHAGE ET BOUCLE PRINCIPALE =====================

COTE_CASES = 100
NOMBRE_DE_CASES = 4
TAILLE_FENETRE = COTE_CASES * NOMBRE_DE_CASES
HAUTEUR_SCORE = 100

# Palette de couleurs en teintes de violet
COULEURS_CASES = {
    2: (235, 224, 255),
    4: (220, 200, 255),
    8: (200, 160, 255),
    16: (180, 130, 255),
    32: (160, 100, 255),
    64: (140, 70, 255),
    128: (120, 50, 255),
    256: (105, 30, 230),
    512: (90, 15, 200),
    1024: (80, 0, 170),
    2048: (70, 0, 140),
}

COULEUR_FOND = (240, 240, 240)
COULEUR_FOND_SCORE = (255, 255, 255)
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)


def dessiner_grille(screen, grille_obj, font_cases, font_score):
    """Dessine la grille, le score et les cases."""
    screen.fill(COULEUR_FOND)

    # Zone du score
    pygame.draw.rect(screen, COULEUR_FOND_SCORE, (0, 0, TAILLE_FENETRE, HAUTEUR_SCORE))
    score_text = font_score.render(f"Score: {grille_obj.score}", True, NOIR)
    score_rect = score_text.get_rect(center=(TAILLE_FENETRE // 2, HAUTEUR_SCORE // 2))
    screen.blit(score_text, score_rect)

    # Cases de la grille
    for i in range(NOMBRE_DE_CASES):
        for j in range(NOMBRE_DE_CASES):
            valeur = grille_obj.grille[i][j]
            couleur = COULEURS_CASES.get(valeur, (60, 58, 50))

            x = j * COTE_CASES
            y = i * COTE_CASES + HAUTEUR_SCORE
            pygame.draw.rect(screen, couleur, (x, y, COTE_CASES, COTE_CASES))
            pygame.draw.rect(screen, NOIR, (x, y, COTE_CASES, COTE_CASES), 1)

            if valeur != 0:
                text_color = NOIR if valeur <= 4 else BLANC
                text = font_cases.render(str(valeur), True, text_color)
                text_rect = text.get_rect(center=(x + COTE_CASES // 2, y + COTE_CASES // 2))
                screen.blit(text, text_rect)

    pygame.display.flip()


def dessiner_game_over(screen, font_go):
    """Affiche le texte Game Over par-dessus la grille."""
    text = font_go.render("Game Over!", True, ROUGE)
    text_rect = text.get_rect(center=(TAILLE_FENETRE // 2, TAILLE_FENETRE // 2 + HAUTEUR_SCORE))
    screen.blit(text, text_rect)
    pygame.display.flip()


async def main():
    pygame.init()
    screen = pygame.display.set_mode((TAILLE_FENETRE, TAILLE_FENETRE + HAUTEUR_SCORE))
    pygame.display.set_caption("2048")

    font_cases = pygame.font.SysFont(None, 40)
    font_score = pygame.font.SysFont(None, 40)
    font_go = pygame.font.SysFont(None, 60)

    grille = Grille()

    # Piles pour Défaire / Refaire
    etats_grille = []
    refaire_grille = []

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not game_over:
                direction = None
                if event.key == pygame.K_LEFT:
                    direction = 'gauche'
                elif event.key == pygame.K_RIGHT:
                    direction = 'droite'
                elif event.key == pygame.K_UP:
                    direction = 'haut'
                elif event.key == pygame.K_DOWN:
                    direction = 'bas'

                if direction:
                    etats_grille.append(grille.cloner())
                    refaire_grille.clear()
                    grille.deplacer(direction)

                # Défaire (Backspace)
                if event.key == pygame.K_BACKSPACE and etats_grille:
                    refaire_grille.append(grille.cloner())
                    ancien = etats_grille.pop()
                    grille.grille = ancien.grille
                    grille.score = ancien.score

                # Refaire (Entrée)
                if event.key == pygame.K_RETURN and refaire_grille:
                    etats_grille.append(grille.cloner())
                    nouveau = refaire_grille.pop()
                    grille.grille = nouveau.grille
                    grille.score = nouveau.score

        dessiner_grille(screen, grille, font_cases, font_score)

        if grille.jeu_termine() and not game_over:
            game_over = True
            dessiner_game_over(screen, font_go)

        await asyncio.sleep(0)  # Indispensable pour Pygbag : permet au navigateur de respirer

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
