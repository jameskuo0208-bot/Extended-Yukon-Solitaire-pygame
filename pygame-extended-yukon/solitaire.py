import pygame
import random
import copy

pygame.init()

clock=pygame.time.Clock()

screenW, screenH=1600, 900
screen=pygame.display.set_mode((screenW, screenH))
pygame.display.set_caption("Extended Yukon Solitaire")

font=pygame.font.SysFont("Arial", 60)
ctrl_font=pygame.font.SysFont("Arial", 40)

bgIMG=pygame.image.load("assets/background.png").convert_alpha()
bgW, bgH=bgIMG.get_size()

titleIMG=pygame.image.load("assets/title.png").convert_alpha()
titleW, titleH=titleIMG.get_size()

playIMG=pygame.image.load("assets/play_button.png").convert_alpha()
quitIMG=pygame.image.load("assets/quit_button.png").convert_alpha()
btn_scale=0.8
playIMG, quitIMG=pygame.transform.scale_by(playIMG, btn_scale), pygame.transform.scale_by(quitIMG, btn_scale)
btnW, btnH=playIMG.get_size()
playBTN=pygame.Rect(screenW/2-btnW/2-400, screenH/2, btnW, btnH)
quitBTN=pygame.Rect(screenW/2+200, screenH/2, btnW, btnH)

rtnIMG=pygame.image.load("assets/return_button.png").convert_alpha()
rtn_scale=0.2
rtnIMG=pygame.transform.smoothscale_by(rtnIMG, rtn_scale)
rtnW, rtnH=rtnIMG.get_size()
rtnBTN=pygame.Rect(screenW-rtnW, 0, rtnW, rtnH)

undoIMG=pygame.image.load("assets/undo_button.png").convert_alpha()
undoIMG=pygame.transform.smoothscale_by(undoIMG, rtn_scale)
undoBTN=pygame.Rect(0, 0, rtnW, rtnH)

ngIMG=pygame.image.load("assets/newgame_button.png").convert_alpha()
ngIMG=pygame.transform.smoothscale_by(ngIMG, rtn_scale)
ngBTN=pygame.Rect(0, screenH-rtnH, rtnW, rtnH)

pauseIMG=pygame.image.load("assets/pause_button.png").convert_alpha()
pauseIMG=pygame.transform.smoothscale_by(pauseIMG, rtn_scale)
pauseBTN=pygame.Rect(screenW-rtnW, screenH-rtnH, rtnW, rtnH)

bg_surface=pygame.Surface((screenW, screenH))

backIMG=pygame.image.load("assets/cards/bg.png").convert_alpha()
card_scale=1/25
backIMG=pygame.transform.smoothscale_by(backIMG, card_scale)
suits=["c", "d", "s", "h"]
cardIMG=[[pygame.image.load(f"assets/cards/{val}{sut}.png").convert_alpha() for val in range(1, 17)] for sut in suits]
cardIMG=[[pygame.transform.smoothscale_by(crd, card_scale) for crd in suit] for suit in cardIMG]
crdW, crdH=backIMG.get_size()

dx = 150
dy = 30
boardW = crdW + dx * 7
x_start = screenW / 2 - boardW / 2
y_start = 100 + crdH

class Card:
    def __init__(self, row, col, suit, value, flipped):
        self.row, self.col=row, col
        self.suit, self.value=suit, value
        self.flipped=flipped
        self.dx, self.dy=dx, dy
        self.x0, self.y0=x_start, y_start
        self.x, self.y=self.x0+self.dx*self.row, self.y0+self.dy*self.col
    def draw(self, gsf):
        if not self.flipped: gsf.blit(backIMG, (self.x, self.y))
        else:
            gsf.blit(cardIMG[suits.index(self.suit)][self.value-1], (self.x, self.y))

history=[]
move_committed=False



emptyFDT, emptyTBL=pygame.image.load("assets/foundation.png").convert_alpha(), pygame.image.load("assets/empty.png").convert_alpha()
emptyFDT, emptyTBL=pygame.transform.smoothscale_by(emptyFDT, card_scale), pygame.transform.smoothscale_by(emptyTBL, card_scale)


tabelau_close_count=[0, 1, 2, 3, 4, 5, 6, 7]
tabelau_open_count=[1, 5, 5, 5, 5, 5, 5, 5]
tabelau=[]

message_sf=pygame.Surface((screenW, screenH))
message_sf.fill((0, 0, 0))
message_sf.set_alpha(85)


gamesurface=pygame.Surface((screenW, screenH))

def save_state():
    state = {
        "tabelau": copy.deepcopy(tabelau),
        "foundations": copy.deepcopy(foundations),
    }
    history.append(state)

for x in range(0, screenW, bgW):
    for y in range(0, screenH, bgH):
        bg_surface.blit(bgIMG, (x, y))


def serve(tbl:list, dck:list):
    tbl.clear()
    for i in range(8):
        cs=[]
        for a in range(tabelau_close_count[i]):
            s, v=dck.pop()
            card=Card(i, a, s, v, False)
            cs.append(card)
        for b in range(tabelau_open_count[i]):
            s, v=dck.pop()
            card=Card(i, tabelau_close_count[i]+b, s, v, True)
            cs.append(card)
        tbl.append(cs)
    return tbl


foundation_pos = []
foundations=[[] for _ in range(4)]


for i in range(4):
    x = x_start + i * dx
    y = 70
    foundation_pos.append((x, y))

tabelau_pos=[(x_start+dx*i, y_start) for i in range(8)]

def draw_foundations():
    for i, pos in enumerate(foundation_pos):
        if not len(foundations[i]):
            gamesurface.blit(emptyFDT, pos)
        else:
            top=foundations[i][-1]
            top.draw(gamesurface)

def draw_empty():
    for i, pos in enumerate(tabelau_pos):
        if not len(tabelau[i]):
            gamesurface.blit(emptyTBL, pos)

def can_move_to_foundation(card, foundation):
    if not len(foundation):
        return card.value==1
    top=foundation[-1]
    return card.suit==top.suit and card.value==top.value+1

def auto_flip(col):
    if len(col) and not col[-1].flipped: col[-1].flipped=True

def get_card_at_pos(pos):
    mx, my = pos

    for i, (fx, fy) in enumerate(foundation_pos):
        if len(foundations[i]):
            card = foundations[i][-1]
            rect = pygame.Rect(card.x, card.y, crdW, crdH)
            if rect.collidepoint(mx, my):
                return ("foundation", i)
        
    for col_idx in reversed(range(len(tabelau))):  # 從右往左
        col = tabelau[col_idx]
        for i in reversed(range(len(col))):        # 從上往下
            card = col[i]
            rect = pygame.Rect(card.x, card.y, crdW, crdH)
            if rect.collidepoint(mx, my) and card.flipped:
                return col_idx, i
    return None, None

def is_red(card):
    return card.suit in ["h", "d"]

def is_black(card):
    return card.suit in ["s", "c"]

def can_move_to_tabelau(moving_card, target_col):
    if len(target_col)==0:
        return moving_card.value==16
    top=target_col[-1]

    if top.value==moving_card.value+1:
        return ((is_red(top) and is_black(moving_card)) or (is_black(top) and is_red(moving_card)))
    return False

def get_card_spacing(col):
    max_spacing = 30  # 平時間距
    min_spacing = 5   # 最小間距
    total_height = 100 + crdH + len(col) * max_spacing
    if total_height > screenH - 50:  # 如果超過螢幕高度
        spacing = max(min_spacing, (screenH - 150 - crdH) / max(1, len(col)))
    else:
        spacing = max_spacing
    return spacing

def layout_column(col, col_idx):
    spacing = get_card_spacing(col)
    for i, c in enumerate(col):
        c.row = col_idx
        c.col = i
        c.x = x_start + dx * col_idx
        c.y = y_start + i * spacing

actions=0

def undo():
    global tabelau, foundations

    if len(history) > 0:
        state = history.pop()
        tabelau = state["tabelau"]
        foundations = state["foundations"]

        for i, col in enumerate(tabelau):
            layout_column(col, i)

        for i, f in enumerate(foundations):
            for c in f:
                c.x, c.y = foundation_pos[i]

def check_win(fdt:list):
    for f in fdt:
        if len(f)!=16: return False
    return True

game_started=False
confirming=False
dragging=False
confirming_ng=False
paused=False
drag_crds=[]
drag_offset_x = 0
drag_offset_y = 0
origin_col = None

win=False

running=True


while running:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT: running=False
            case pygame.MOUSEBUTTONDOWN:
                if not game_started:
                    if playBTN.collidepoint(event.pos):
                        game_started=True
                        deck=[(s, v) for s in suits for v in range(1, 17)]
                        random.shuffle(deck)
                        foundations=[[] for _ in range(4)]
                        serve(tabelau, deck)
                    elif quitBTN.collidepoint(event.pos):
                        running=False
                else:
                    if rtnBTN.collidepoint(event.pos):
                        confirming=True
                    elif confirming:
                        confirming=False
                        continue

                    if confirming:
                        continue

                    if ngBTN.collidepoint(event.pos):
                        confirming_ng=True
                    elif confirming_ng:
                        confirming_ng=False
                        continue
                    
                    if confirming_ng:
                        continue

                    if pauseBTN.collidepoint(event.pos):
                        paused=True
                    elif paused:
                        paused=False
                        continue
                    if paused: continue

                    if len(history) and not dragging:
                        if undoBTN.collidepoint(event.pos):
                            undo()
                            actions-=1
                    result = get_card_at_pos(event.pos)

                    col_idx = None
                    card_idx = None

                    if result[0] == "foundation":
                        f_idx = result[1]
                        save_state()
                        move_committed=False
                        dragging = True
                        origin_col = ("foundation", f_idx)

                        drag_crds = [foundations[f_idx].pop()]

                        card = drag_crds[0]
                        drag_offset_x = event.pos[0] - card.x
                        drag_offset_y = event.pos[1] - card.y
                        drag_offsets = [(0, 0)]

                    elif result[0] is not None:
                        col_idx, card_idx = result
                        save_state()
                        move_committed=False
                        dragging = True
                        origin_col = col_idx

                        drag_crds = tabelau[col_idx][card_idx:]
                        tabelau[col_idx] = tabelau[col_idx][:card_idx]

                        card = drag_crds[0]
                        drag_offset_x = event.pos[0] - card.x
                        drag_offset_y = event.pos[1] - card.y
                        drag_offsets = [(c.x-drag_crds[0].x, c.y-drag_crds[0].y) for c in drag_crds]
            case pygame.MOUSEBUTTONUP:
                if dragging:
                    mx, my=event.pos
                    placed=False
                    move_committed=False
                    for col_idx in range(len(tabelau)):
                        col=tabelau[col_idx]
                        if not len(col):
                            target_x=x_start+dx*col_idx
                            target_y=y_start
                        else:
                            last=col[-1]
                            target_x, target_y=last.x, last.y
                        rect=pygame.Rect(target_x, target_y, crdW, crdH)
                        if rect.collidepoint(mx, my):
                            if can_move_to_tabelau(drag_crds[0], col):
                                move_committed=True
                                new_col=col+drag_crds
                                tabelau[col_idx]=new_col
                                layout_column(new_col, col_idx)
                                actions+=1
                                placed=True
                                break
                    if not placed and len(drag_crds)==1:
                        for i, (fx, fy) in enumerate(foundation_pos):
                            rect=pygame.Rect(fx, fy, crdW, crdH)
                            if rect.collidepoint(mx, my):
                                if can_move_to_foundation(drag_crds[0], foundations[i]):
                                    move_committed=True
                                    card=drag_crds[0]
                                    actions+=1
                                    card.x, card.y=fx, fy
                                    foundations[i].append(card)
                                    placed=True
                                    break
                    if not placed:
                        if not move_committed and len(history): history.pop()
                        if isinstance(origin_col, tuple):  # 來自 foundation
                            f_idx = origin_col[1]
                            foundations[f_idx].append(drag_crds[0])
                            drag_crds[0].x, drag_crds[0].y = foundation_pos[f_idx]
                        else:
                            new_col = tabelau[origin_col] + drag_crds
                            tabelau[origin_col] = new_col
                            layout_column(new_col, origin_col)

                    # ⭐只對 tableau 做 auto flip
                    if not isinstance(origin_col, tuple):
                        auto_flip(tabelau[origin_col])
                    dragging=False
                    drag_crds=[]
            case pygame.MOUSEMOTION:
                if dragging:
                    mx, my=event.pos
                    for i, c in enumerate(drag_crds):
                        c.x=mx-drag_offset_x+drag_offsets[i][0]
                        c.y=my-drag_offset_y+drag_offsets[i][1]
            case pygame.KEYDOWN:
                if confirming:
                    match event.key:
                        case pygame.K_y:
                            game_started=False
                            confirming=False
                            win=False
                            confirming_ng=False
                            paused=False
                            history=[]
                        case pygame.K_n:
                            confirming=False
                if confirming_ng:
                    match event.key:
                        case pygame.K_y:
                            deck = [(s, v) for s in suits for v in range(1, 17)]
                            random.shuffle(deck)

                            foundations = [[] for _ in range(4)]
                            tabelau.clear()
                            serve(tabelau, deck)

                            for i, col in enumerate(tabelau):
                                layout_column(col, i)

                            win=False
                            confirming=False
                            confirming_ng=False
                            paused=False
                            dragging=False
                            drag_crds=[]
                            history=[]
                        case pygame.K_n:
                            confirming_ng=False

                if win:
                    match event.key:
                        case pygame.K_x:
                            running=False
                        case pygame.K_r:
                            deck = [(s, v) for s in suits for v in range(1, 17)]
                            random.shuffle(deck)

                            foundations = [[] for _ in range(4)]
                            tabelau.clear()
                            serve(tabelau, deck)

                            for i, col in enumerate(tabelau):
                                layout_column(col, i)

                            win=False
                            confirming=False
                            confirming_ng=False
                            dragging=False
                            drag_crds=[]
                            history=[]
    if not game_started: 
        gamesurface.blit(bg_surface, (0, 0))
        gamesurface.blit(titleIMG, (screenW/2-titleW/2, screenH/2-titleH/2-btnH))
        gamesurface.blit(playIMG, (screenW/2-btnW/2-400, screenH/2))
        gamesurface.blit(quitIMG, (screenW/2+200, screenH/2))
    else:
        gamesurface.blit(bg_surface, (0, 0))
        gamesurface.blit(rtnIMG, (screenW-rtnW, 0))
        gamesurface.blit(ngIMG, (0, screenH-rtnH))
        gamesurface.blit(pauseIMG, (screenW-rtnW, screenH-rtnH))
        draw_foundations()
        draw_empty()
        for col_idx, col in enumerate(tabelau):
            for card in col:
                if card not in drag_crds:
                    card.draw(gamesurface)

        for card in drag_crds:
            card.draw(gamesurface)
        if actions>0:
            gamesurface.blit(undoIMG, (0, 0))
        if confirming:
            gamesurface.blit(message_sf, (0, 0))
            cfm_txt=font.render("Are you sure?", True, (255, 255, 255))
            cfm_rct=cfm_txt.get_rect()
            cfmW, cfmH=cfm_rct.size
            ctrl_txt=ctrl_font.render("Press Y for yes. Press N or click anywhere for no.", True, (255, 255, 255))
            ctrl_rct=ctrl_txt.get_rect()
            ctrW, ctrH=ctrl_rct.size
            gamesurface.blit(cfm_txt, (screenW/2-cfmW/2, screenH/2-(cfmH+ctrH)/2))
            gamesurface.blit(ctrl_txt, (screenW/2-ctrW/2, screenH/2-(cfmH+ctrH)/2+cfmH))
        if confirming_ng:
            gamesurface.blit(message_sf, (0, 0))
            cfm_txt=font.render("Are you sure?", True, (255, 255, 255))
            cfm_rct=cfm_txt.get_rect()
            cfmW, cfmH=cfm_rct.size
            ctrl_txt=ctrl_font.render("Press Y for yes. Press N or click anywhere for no.", True, (255, 255, 255))
            ctrl_rct=ctrl_txt.get_rect()
            ctrW, ctrH=ctrl_rct.size
            gamesurface.blit(cfm_txt, (screenW/2-cfmW/2, screenH/2-(cfmH+ctrH)/2))
            gamesurface.blit(ctrl_txt, (screenW/2-ctrW/2, screenH/2-(cfmH+ctrH)/2+cfmH))
        if paused:
            gamesurface.blit(message_sf, (0, 0))
            pause_txt=font.render("GAME PAUSED", True, (255, 255, 255))
            pause_rct=pause_txt.get_rect()
            pauseW, pauseH=pause_rct.size
            msg_txt=ctrl_font.render("Click anywhere to resume your game", True, (255, 255, 255))
            msg_rct=msg_txt.get_rect()
            msgW, msgH=msg_rct.size
            gamesurface.blit(pause_txt, (screenW/2-pauseW/2,  screenH/2-(pauseH+msgH)/2))
            gamesurface.blit(msg_txt, (screenW/2-msgW/2, screenH/2-(pauseH+msgH)/2+pauseH))
        if check_win(foundations):
            win=True
            gamesurface.blit(message_sf, (0, 0))
            win_txt=font.render("YOU WON!", True, (255, 255, 255))
            win_rct=win_txt.get_rect()
            winW, winH=win_rct.size
            msg_txt1=ctrl_font.render("Press R to replay", True, (255, 255, 255))
            msg_txt2=ctrl_font.render("Press X to quit", True, (255, 255, 255))
            msg1_rct=msg_txt1.get_rect()
            msg2_rct=msg_txt2.get_rect()
            mw1, mh1=msg1_rct.size
            mw2, mh2=msg2_rct.size
            gamesurface.blit(win_txt, (screenW/2-winW/2, screenH/2-(winH+mh1+mh2)/2))
            gamesurface.blit(msg_txt1, (screenW/2-mw1/2, screenH/2-(winH+mh1+mh2)/2+winH))
            gamesurface.blit(msg_txt2, (screenW/2-mw2/2, screenH/2-(winH+mh1+mh2)/2+winH+mh1))
    screen.blit(gamesurface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()