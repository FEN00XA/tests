
import sys
import pygame

from game import ChessGame


def main():
    
    pygame.init()

    
    game = ChessGame()
    
    
    clock = pygame.time.Clock()
    running = True
 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #print(" Game window closed by user")
                running = False
            else:
                game.handle_event(event)
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
