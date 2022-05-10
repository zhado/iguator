import pygame
from pygame.locals import *
import os
import subprocess
import shlex
Width = Height = 0

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("audio2.ogg")
scr = pygame.display.set_mode((600, 500),RESIZABLE)
pygame.scrap.init()
running = True
pictures=tuple(os.walk("./pics"))[0][2]
smallfont = pygame.font.SysFont('Arial',30) 
smolfont = pygame.font.SysFont('Arial',15) 

current_picture=0

playing=False
show_final=True
replace=True
start_timestamp=0
start_time=0
zoom_factor=4
time_multiplier=2
initial_offset=17*60*60+15*60
posx=0
posy=0
mousedown=False
take_screenshot=False
selection=[0,0,0,0]
loaded=[]

def secs_to_ts(in_secs):
    secs=in_secs%60
    mins=(in_secs/(60))%60
    hours=in_secs/(60*60)
    return str('%02d' % hours)+":"+str('%02d' %mins)+":"+str('%02d' % secs)

class slides:
    def __init__(self):
        self.current_active=0
        self.slide_view_offset=0
        self.images=[]
        self.timestamps=[]
    def add(self,screen,rect,time=0):
        if(selection[2]!=0 and selection[3]!=0):
            if selection[2]>selection[0]:
                selection[2],selection[0]=selection[0],selection[2]
            if selection[3]<selection[1]:
                selection[3],selection[1]=selection[1],selection[3]
            rect=[rect[0]+2,rect[1]+2,abs(rect[2]-rect[0]-3),abs(rect[3]-rect[1]-3)]
            rec=pygame.Rect(rect[0],rect[1],rect[2],rect[3])
            self.images.insert(self.current_active,screen.subsurface(rec).copy())
        else:
            self.images.insert(self.current_active,loaded[current_picture])
        if(time==0 and len(self.images)!=1):
            if playing:
                self.timestamps.insert(self.current_active,start_timestamp+(pygame.time.get_ticks()-start_time)/1000)
            else:
                self.timestamps.insert(self.current_active,self.timestamps[self.current_active-1])
        else:
            self.timestamps.insert(self.current_active,time)
        self.current_active+=1
    def change(self,screen,rect,time=0):
        if(selection[2]!=0 and selection[3]!=0):
            rect=[rect[0]+2,rect[1]+2,rect[2]-rect[0]-3,rect[3]-rect[1]-3]
            rec=pygame.Rect(rect[0],rect[1],rect[2],rect[3])
            self.images[self.current_active-1]=screen.subsurface(rec).copy()
        else:
            self.images[self.current_active-1]=loaded[current_picture]
        if(time==0 and len(self.images)!=1):
            if playing:
                self.timestamps[self.current_active-1]=start_timestamp+(pygame.time.get_ticks()-start_time)/1000
            else:
                self.timestamps[self.current_active-1]=self.timestamps[self.current_active-1]
        else:
            self.timestamps[self.current_active-1]=time
    def render_frame(self,index):
        export_surface=pygame.Surface((1920, 1080))
        img=self.images[index]
        width, height =img.get_size()
        x_scale=1920/width
        y_scale=1080/height
        if x_scale<y_scale:
            fin_scale=x_scale
        else:
            fin_scale=y_scale
        export_surface.fill((0, 0, 0))
        img = pygame.transform.smoothscale(img,(int(width*fin_scale),int(height*fin_scale)))
        export_surface.blit(img,[1920/2-(width*fin_scale)/2,1080/2-(height*fin_scale)/2])
        return export_surface

    def draw(self,scr):
        last_y=0
        bottom_offset=80
        self.slide_view_offset=int((self.current_active-1)/(Width/40))*(Width/40)
        for count, img in enumerate(self.images):
            if(count >= self.slide_view_offset):
                pygame.draw.rect(scr, (0, 0, 255), (last_y,Height-bottom_offset,35,30))
                text = smallfont.render(str(count) , True , (255,0,0)) 
                scr.blit(text,[last_y,Height-bottom_offset])
                if(count==self.current_active-1):
                    pygame.draw.rect(scr, (0, 255, 0), (last_y-4,Height-4-bottom_offset,35+8,30+8),4)
                    text = smallfont.render(secs_to_ts(self.timestamps[self.current_active-1]) , True , (0,0,0)) 
                    scr.blit(text,[0,Height-30])
                    if show_final:
                        big_render=self.render_frame(count)
                        img = pygame.transform.smoothscale(big_render,(int(1920/2),int(1080/2)))
                        scr.blit(img,[Width/2,0])

                last_y+=40


    def export(self):
        f = open("./export/input", "w")
        lastcount=0
        print("exporting...")
        for count, img in enumerate(self.images):
            print(count)
            pygame.image.save(self.render_frame(count),"./export/"+str(count)+".png")
            f.write("file " + "\'"+"./"+str(count)+".png"+"\'"+"\n")
            current_timestamp=self.timestamps[count]
            next_timestamp=self.timestamps[(count+1)%len(self.images)]
            delta=(next_timestamp-current_timestamp)*time_multiplier
            if delta ==0:
                delta =1
            f.write("duration " + str(abs(delta))+"\n")
            lastcount=count
        f.write("file " + "\'"+"./"+str(count)+".png"+"\'"+"\n")
        f.close()

        # command="ffmpeg -y -f concat -safe 0 -i ./export/input -i audio.ogg -vsync cfr -r 2 -pix_fmt yuv420p -acodec copy ./export/output.mp4"
        # command=shlex.split(command)
        # with open('./export/test.log', 'wb') as f: 
            # process = subprocess.Popen(command, stdout=subprocess.PIPE)
            # for c in iter(lambda: process.stdout.read(1), b''): 
                # sys.stdout.buffer.write(c)
                # f.buffer.write(c)
        print("done")

c_slides=slides()

for image in pictures:
    loaded.append(pygame.image.load("./pics/"+image))

def draw_current_image(scr):
    text = smallfont.render(str(str(current_picture+1)+"/"+str(len(loaded))) , True , (255,0,0)) 
    width, height =loaded[current_picture].get_size()
    img = pygame.transform.scale(loaded[current_picture],(int(width/zoom_factor),int(height/zoom_factor)))
    scr.blit(img,[50,0])
    scr.blit(text,[0,0])
    if playing:
        play_time = smallfont.render(secs_to_ts(start_timestamp+(pygame.time.get_ticks()-start_time)/1000) , True , (0,0,0)) 
        scr.blit(play_time,[0,Height-120])
        play_time2 = smallfont.render(secs_to_ts((start_timestamp+(pygame.time.get_ticks()-start_time)/1000)*time_multiplier) , True , (0,0,0)) 
        scr.blit(play_time2,[0,Height-150])
        play_time3 = smallfont.render(secs_to_ts((start_timestamp+(pygame.time.get_ticks()-start_time)/1000)*time_multiplier+initial_offset) , True , (0,0,0)) 
        scr.blit(play_time3,[0,Height-180])

while running:
    scr.fill((255, 255, 255))
    Width, Height = pygame.display.get_surface().get_size()
    for e in pygame.event.get():
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            selection[2], selection[3] = pygame.mouse.get_pos()
            # posx, posy = e.pos

        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN :
            mousedown=True
            selection[0], selection[1] = pygame.mouse.get_pos()

        # clear selection
        if e.type == pygame.KEYDOWN and e.key==pygame.K_q:
            selection=[0,0,0,0]
        # hide final render
        if e.type == pygame.KEYDOWN and e.key==pygame.K_h:
            show_final=not show_final
        # capture selection
        if e.type == pygame.KEYDOWN and e.key==pygame.K_c and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            take_screenshot=True
            replace=False
        if e.type == pygame.KEYDOWN and e.key==pygame.K_c and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            take_screenshot=True
            replace=True
        # zoom in
        if e.type == pygame.KEYDOWN and e.key==pygame.K_z and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            zoom_factor=zoom_factor/2
        # zoom out 
        if e.type == pygame.KEYDOWN and e.key==pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            zoom_factor=zoom_factor*2
        # paste image from clipboard
        if e.type == pygame.KEYDOWN and e.key==pygame.K_p:
            os.system("wl-paste > temp.png")
            loaded.append(pygame.image.load("./temp.png"))
            current_picture=len(loaded)-1
        # play/pause audio
        if e.type == pygame.KEYDOWN and e.key==pygame.K_SPACE:
            if playing:
                pygame.mixer.music.stop()
                playing=False
            else:
                start_timestamp=c_slides.timestamps[c_slides.current_active-1]
                start_time=pygame.time.get_ticks()
                pygame.mixer.music.play(start=start_timestamp)
                playing=True
        # export
        if e.type == pygame.KEYDOWN and e.key==pygame.K_e:
            c_slides.export()
        if e.type == pygame.KEYDOWN and e.key==pygame.K_LEFT and current_picture!=0 and not pygame.key.get_mods() & pygame.KMOD_CTRL: 
            current_picture -= 1 
        if e.type == pygame.KEYDOWN and e.key==pygame.K_RIGHT and current_picture<len(loaded)-1 and not pygame.key.get_mods() & pygame.KMOD_CTRL:  
            current_picture += 1 
        if e.type == pygame.KEYDOWN and e.key==pygame.K_LEFT and c_slides.current_active>1 and pygame.key.get_mods() & pygame.KMOD_CTRL: 
            c_slides.current_active -= 1 
        if e.type == pygame.KEYDOWN and e.key==pygame.K_RIGHT and c_slides.current_active!=len(c_slides.images) and pygame.key.get_mods() & pygame.KMOD_CTRL: 
            c_slides.current_active += 1 


        if e.type == pygame.MOUSEBUTTONUP:
            mousedown=False
            selection[2], selection[3] = e.pos
    keys=pygame.key.get_pressed()
    if keys[pygame.K_UP] and not pygame.key.get_mods() & pygame.KMOD_CTRL:
        c_slides.timestamps[c_slides.current_active-1]+=1;
        pygame.time.wait(25)

    if keys[pygame.K_DOWN] and c_slides.timestamps[c_slides.current_active-1]>0 and c_slides.timestamps[c_slides.current_active-1] > c_slides.timestamps[c_slides.current_active-2] and not pygame.key.get_mods() & pygame.KMOD_CTRL:
        c_slides.timestamps[c_slides.current_active-1]-=1;
        pygame.time.wait(25)

    if keys[pygame.K_UP] and pygame.key.get_mods() & pygame.KMOD_CTRL:
        initial_offset+=1
        pygame.time.wait(25)

    if keys[pygame.K_DOWN] and pygame.key.get_mods() & pygame.KMOD_CTRL:
        initial_offset-=1
        pygame.time.wait(25)

    c_slides.draw(scr)
    draw_current_image(scr)
    pygame.draw.rect(scr, (200, 0, 0), (selection[0], selection[1],selection[2]-selection[0],selection[3]-selection[1]),2)

    if(take_screenshot):
            if replace:
                c_slides.change(scr,selection)
            else:
                c_slides.add(scr,selection)
            take_screenshot=False

    pygame.display.flip()
pygame.quit()
