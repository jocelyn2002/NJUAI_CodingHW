#include <game.h>

#define FPS 20
#define SIDE 16


// 全局变量定义
int w,h; //　屏幕大小
int is_on;
int is_restart;
int snake[1200][2];
int block[1200];
int length;
int direction;
int is_apple;
int apple[2];
int head[2];// 当前头坐标
int tail[2];// 上一个时刻的尾坐标

// 工具,不超过两倍之内取模
int mod(int a,int m) {
  while (a<0) a+=m;
  while (a>=m) a-=m;
  return a;
}
// 工具,绘制纯色矩形
void draw_tile(int x, int y, int w, int h, uint32_t color) {
  uint32_t pixels[w * h]; // careful! stack is limited!
  _DEV_VIDEO_FBCTRL_t event = {
    .x = x, .y = y, .w = w, .h = h, .sync = 1,
    .pixels = pixels,
  };
  for (int i = 0; i < w * h; i++) {
    pixels[i] = color;
  }
  _io_write(_DEV_VIDEO, _DEVREG_VIDEO_FBCTRL, &event, sizeof(event));
}
// 工具,清屏
void clear(uint32_t color) {
  for (int x = 0; x * SIDE <= w; x ++) {
    for (int y = 0; y * SIDE <= h; y++) {
      draw_tile(x * SIDE, y * SIDE, SIDE, SIDE, color); // white
    }
  }
}

// 初始化游戏
void init_game() {
  is_on = 1;
  is_restart = 0;
  direction = _KEY_RIGHT;
  length = 1;
  snake[0][0]=snake[0][1]=0;
  is_apple = 0;
  for (int i=0;i<1200;i++) block[i]=0;
  block[0]=1;
  draw_tile(0,0,SIDE,SIDE,0xffffff);
  printf("开始游戏!\n");
}
// 处理键盘事件
void kbd_event(int key) {
  switch (key) {
    case _KEY_ESCAPE:_halt(0);break;
    case _KEY_UP: direction=_KEY_UP;break;
    case _KEY_DOWN: direction = _KEY_DOWN;break;
    case _KEY_LEFT: direction = _KEY_LEFT;break;
    case _KEY_RIGHT: direction = _KEY_RIGHT;break;
    case _KEY_SPACE: if (is_on==0) is_restart = 1;break;
  } 
}
// 处理一帧游戏逻辑
void generate_apple() {
  int ran = mod(rand(),w/SIDE*h/SIDE-length);
  int i = 0,num = 0;
  for (;i<w/SIDE*h/SIDE && num<ran;i++) {
    if (block[i] == 0) num++;
  }
  apple[0]=mod(i,w/SIDE)*SIDE;
  apple[1]=i/(w/SIDE)*SIDE;
  is_apple = 1;
  draw_tile(apple[0],apple[1],SIDE,SIDE,0xccff66);
}
int is_dead() {
  for (int i=0;i<length-1;i++) {
    if (snake[i][0]*SIDE==head[0]&&snake[i][1]*SIDE==head[1])
      return 1;
  }
  return 0;
}
void game_progress(){
  if (is_on == 0) {
    if (is_restart==1) {
      clear(0);
      init_game();
    }
  }
  else {
    switch (direction) {
      case _KEY_UP: 
        snake[length][0]=snake[length-1][0];
        snake[length][1]=mod(snake[length-1][1]-1,h/SIDE);
        break;
      case _KEY_DOWN:
        snake[length][0]=snake[length-1][0];
        snake[length][1]=mod(snake[length-1][1]+1,h/SIDE);
        break;
      case _KEY_LEFT:
        snake[length][0]=mod(snake[length-1][0]-1,w/SIDE);
        snake[length][1]=snake[length-1][1];
        break;
      case _KEY_RIGHT:
        snake[length][0]=mod(snake[length-1][0]+1,w/SIDE);
        snake[length][1]=snake[length-1][1];
        break;
    }
    length++;

    head[0]=snake[length-1][0]*SIDE;
    head[1]=snake[length-1][1]*SIDE;
    tail[0]=snake[0][0]*SIDE;
    tail[1]=snake[0][1]*SIDE;

    // printf("head:(%d,%d)  tail:(%d,%d)",head[0],head[1],tail[0],tail[1]);
    if (snake[length-1][0]*SIDE==apple[0] && snake[length-1][1]*SIDE==apple[1]) {
      draw_tile(head[0],head[1],SIDE,SIDE,0xffffff);
      block[head[0]/SIDE+head[1]*(w/SIDE)/SIDE]=1;
      is_apple = 0;
      printf("length: %d  ",length);
      printf("apple: %d, %d\n",apple[0]/SIDE,apple[1]/SIDE);
    }// 吃苹果,尾部不缩短,只长头
    else if (is_dead()) {
      clear(0xccff66);
      printf("YOU DIED!!! press SPACE to restart!!!\n");
      is_on = 0;
    }// 死了,进入等待界面
    else {
      draw_tile(head[0],head[1],SIDE,SIDE,0xffffff);
      draw_tile(tail[0],tail[1],SIDE,SIDE,0);
      block[head[0]/SIDE+head[1]*(w/SIDE)/SIDE]=1;
      block[tail[0]/SIDE+tail[1]*(w/SIDE)/SIDE]=0;
      for (int j=0;j<=length-2;j++) {
        snake[j][0]=snake[j+1][0];
        snake[j][1]=snake[j+1][1];
      }
      length--;
    }// 没吃到苹果,长头,缩尾
    if (is_apple==0) 
      generate_apple();
  }
}


int main(const char *args) {
  // printf("fuckfuckfuck\n");
  _ioe_init();

  
  // puts("mainargs = \"");
  // puts(args); // make run mainargs=xxx
  // puts("\"\n");


  w = screen_width();
  h = screen_height();
  init_game();

  int next_frame = 0;
  int key=0;

  while (1) {
    while (uptime() < next_frame) {// 等待一帧的到来
      if ((key = read_key()) != _KEY_NONE) {
        kbd_event(key);         // 处理键盘事件
        // printf("fuck %d\n",key);
      }
    }
    
    game_progress();          // 处理游戏逻辑并重新绘制屏幕
    next_frame += 1000 / FPS; // 计算下一帧的时间
  }
  return 0;
}