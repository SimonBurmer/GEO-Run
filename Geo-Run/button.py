import  pygame as pg
from settings import  *

# Default button images/pygame.Surfaces.
IMAGE_NORMAL = pg.Surface((100, 32))
IMAGE_NORMAL.fill(WHITE)
IMAGE_HOVER = pg.Surface((100, 32))
IMAGE_HOVER.fill(GREY)
IMAGE_DOWN = pg.Surface((100, 32))
IMAGE_DOWN.fill(BLACK)

class Button(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, callback, Fontsize, text, text_color=(0, 0, 0),image_normal=IMAGE_NORMAL, image_hover=IMAGE_HOVER,
                image_down=IMAGE_DOWN):
        super().__init__()

        # Scale the images to the desired size (doesn't modify the originals).
        self.image_normal = pg.transform.scale(image_normal, (width, height))
        self.image_hover = pg.transform.scale(image_hover, (width, height))
        self.image_down = pg.transform.scale(image_down, (width, height))

        #The currently active image.
        self.image = self.image_normal  

        #The possition of the button
        self.rect = self.image.get_rect(topleft=(x, y))

        #To center the text rect.
        font = pg.font.SysFont(None, Fontsize)
        image_center = self.image.get_rect().center
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=image_center)

        # Blit the text onto the images.
        for image in (self.image_normal, self.image_hover, self.image_down):
            image.blit(text_surf, text_rect)

        # This function will be called when the button gets pressed.
        self.callback = callback
        self.button_down = False

    #To handle events from the pygame event queue
    def handle_event(self, event):
        #if the mousbutton is pressed down
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.button_down = True

        #if the mousbutton is up 
        elif event.type == pg.MOUSEBUTTONUP:
            # If the rect collides with the mouse pos.
            if self.rect.collidepoint(event.pos) and self.button_down:
                self.callback()  # Call the function.
                self.image = self.image_hover
            self.button_down = False
        
        #if the Mouse is over the button
        elif event.type == pg.MOUSEMOTION:
            collided = self.rect.collidepoint(event.pos)
            if collided and not self.button_down:
                self.image = self.image_hover
            elif not collided:
                self.image = self.image_normal

