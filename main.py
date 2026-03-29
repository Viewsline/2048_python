import asyncio
from graphics_2048 import Jeu2048

async def main():
    jeu = Jeu2048()
    await jeu.jouer()

if __name__ == "__main__":
    asyncio.run(main())
