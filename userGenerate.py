import os

from pynput.mouse import Button, Controller
from random import randint
import pandas as pd
import time
time.sleep(3)
mouse = Controller()
print(mouse.position)
mouse.position = (400, 400)

mouse.press(Button.left)
mouse.release(Button.left)

def mouse_Listener():
    def on_move(x, y):
        print('Pointer moved to {o}'.format(
            (x, y)))
    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
        if not pressed:
            return False
    def on_scroll(x, y, dx, dy):
        print('scrolled {0} at {1}'.format(
            'down' if dy < 0 else 'up',
            (x, y)))
    while True:
        with mouse.Listener(no_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

from pynput.keyboard import Key, Controller
keyboard = Controller()
funcKeys = dir(Key)

def Enter():
    keyboard.press(Key.enter)
    time.sleep(0.1)
    keyboard.release(Key.enter)
    time.sleep(0.1)

def char(c):
    keyboard.press(c)
    keyboard.release(c)

def nano_exit():
   time.sleep(3)
   keyboard.press(Key.ctrl)
   keyboard.press('o')
   keyboard.release('o')
   keyboard.release(Key.ctrl)
   time.sleep(0.1)
   Enter()
   time.sleep(0.1)
   keyboard.press(Key.ctrl)
   keyboard.press('x')
   keyboard.release('x')
   keyboard.release(Key.ctrl)

def cmd(x,time_gap=0.4):
    if type(x) == str:
        if x in funcKeys:
            keyboard.press(x)
            keyboard.release(x)
        else:
            print(x)
            keyboard.type(x)
        Enter()
        time.sleep(time_gap)
    elif type(x) == list:
        for s in x:
            if s in funcKeys:
                keyboard.press(s)
                keyboard.release(s)
            else:
                keyboard.type(s)
            Enter()
            time.sleep(time_gap)

def screen_command(name, command, type='load',gap=0.3):
    if type.lower() == 'load':
        cmd('screen -S %s' % name)
        cmd(command,gap)
        keyboard.press(Key.ctrl)
        time.sleep(0.1)
        keyboard.press('a')
        time.sleep(0.1)
        keyboard.press('d')
        time.sleep(1)
        keyboard.release('a')
        keyboard.release('d')
        keyboard.release(Key.ctrl)
    elif type.lower() == 'exit':
        cmd('screen -r %s' % name, 2)
        keyboard.type(command)
        keyboard.press(Key.ctrl)
        time.sleep(0.1)
        keyboard.press('c')
        time.sleep(0.1)
        keyboard.release('c')
        keyboard.release(Key.ctrl)
        time.sleep(0.1)
        cmd('exit')
        time.sleep(0.2)

def InstallSoftware():
    cmd('./ssh.sh 7',2)
    cmd('cd /home/zzb/',0.1)
    # for i in range(2, 17):
    #     if i == 7 or i == 4 or i == 9 or i==8:
    #         continue
    #     screen_command('scp%s' % i,'','exit', 1 )

    for i in range(16,17):
        if i==4 or i==9 or i==8:
            continue
        cmd('cd /home/zzb/')
        cmd('ssh zzb@11.11.11.%s'%i,1)
        cmd('sudo bash Anaconda3-5.2.0-Linux-x86_64.sh')
        time.sleep(1)
        passwd()
        time.sleep(2)
        Enter()
        cmd(' ',2)
        cmd('yes',2)
        Enter()
        time.sleep(180)
        cmd('no',1)
        cmd('no',1)
        cmd('cd anaconda3/bin/',1)
        cmd('./conda activate',2)
        cmd('echo ". /home/zzb/anaconda3/etc/profile.d/conda.sh" >> ~/.bashrc')
        cmd('echo "conda activate" >> ~/.bashrc')
        cmd('exit',2)

def passwd(password = 'zzb12344321',timegap = 0.2):
    time.sleep(timegap)
    for s in password:
        time.sleep(0.1)
        char(s)
    Enter()
    time.sleep(timegap)

def add_user():
    user_name_passwd_node = [['tmp','tmp_port%s'%(50000+x), x, 'yes'] for x in range(12,17) if x != 4]
    for x in user_name_passwd_node:
        cmd('cd /home/zzb')
        cmd('ssh zzb@11.11.11.%s'%x[2],2)
        passwd()
        auth_auto()
        time.sleep(1)
        cmd('sudo adduser %s'%x[0],1)
        passwd()
        passwd(x[1])
        time.sleep(1)
        passwd(x[1])
        time.sleep(1)
        for i in range(10):
            Enter()
        # if x[3] == 'yes' or x[3] == '是':
        #     keyboard.type('sudo nano /etc/sudoers')
        #     time.sleep(2)
        #     Enter()
        #     passwd()
        #     for i in range(60):
        #         time.sleep(0.05)
        #         keyboard.press(Key.down)
        #         keyboard.release(Key.down)
        #     keyboard.type('%s   ALL=(ALL:ALL) ALL'%x[0])
        #     nano_exit()
        # time.sleep(1)
        keyboard.type('exit')
        Enter()

def passwd_generate(length=20):
    alpha = 'qwertyuiopasdfghjklzxcvbnm'
    ALPHA = alpha.upper()
    digit = '1234567890'
    char = '_.*&^%$#@!~()_+-='
    types = [ALPHA, alpha, digit, char]
    pd = ''
    for x in range(length):
        type = randint(1,1000)%4
        pd += types[type][randint(1,1000)%len(types[type])]
    return pd


def auth_auto():
    cmd('cd ~/.ssh/',1)
    cmd('echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyv0suPB9op6Ilc2A5e7MlD0nHFzV/RvnGjwBdjpYhtCLLfcbvI7JLWYq1aZ2BeEOYSwA2GhLvjdSwVrG95lb6pInE42pd/lOC1B+PRhWB/h7MvaLZJftiUGIrSP6zlRnklouHbLkXe8H5gXlckpGHZ0asuJnVsTJ7J+8OkjSjaPLChhtFeyx5jiBcibO8X09EI6WvC0k4XghqKE+dl2jO8eDsLOJdr4nYoJMgaeaXeJ5HYi2fFAyMVget2zJt1QJtJU1jnrTOAO6mnqnRnYzVH1fFT9UJumcr3x5MSv3lyCuEvPxfegTJFQ5MnmkWWEWcB5EKSqiXlpyqNurmwtOP zzb@node7 >> authorized_keys', 2)
    cmd('cd /home/zzb',0.2)


def check_top():
    for i in range(3,17):
        # if i==8 or i==4 or i==1:
        #     continue
        print("现在准备检查%s号节点" % i)
        cmd('s %s' % i, 1)
        time.sleep(1)
        cmd('top')
        for i in range(10):
            Enter()
            time.sleep(0.1)
        time.sleep(1)
        # pd = passwd_generate(20+randint(-5,10))
        cmd('exit', 1)
        time.sleep(2)


def change_root_passwd(save_dir = '/Users/zhangzhaobo/Documents/GroupFile/server_log/root_passwd.txt'):
    with open(save_dir, 'a', encoding='utf8') as pdlog:
        for i in [16]:
            # if i==8 or i==4 or i==1:
            #     continue
            print("现在准备加密%s号节点，3秒准备"%i)
            time.sleep(1)
            cmd('cd /home/zzb')
            time.sleep(1)
            cmd('ssh zzb@11.11.11.%s' % i, 1)
            passwd()
            # auth_auto()
            time.sleep(1)
            cmd('passwd',1)
            # passwd()
            time.sleep(1)
            # pd = passwd_generate(20+randint(-5,10))
            pd = 'zzb_%s000%s'%(i,i)
            print("准备修改的密码是：%s"%pd)
            passwd(pd)
            time.sleep(0.3)
            passwd(pd)
            pdlog.write("Passwd of :%s"%str(i) + '\t' + pd+'\n')
            cmd('exit',2)


def add_etf():
    all_etf = os.listdir('Strategy/etf_cache')
    for e in all_etf:
        data = pd.read_csv('Strategy/etf_cache/%s' % e)
        if e[:6] =='510050' or e[:6] =='588000':
            continue
        try:
            if data.iloc[0, :]['vol'] < 10000 or data.iloc[0, :]['close'] > 10 or data.iloc[0, :]['close'] < 0.5:
                continue
            if data.iloc[0, :]['vol'] > 50000:
                continue
        except Exception as x:
            continue
        else:
            mouse.position = (1026, 1131)
            time.sleep(0.5)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(0.5)
            cmd(e[:6],1)
            time.sleep(0.5)
            mouse.position = (1834, 1202)
            time.sleep(1)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(1)
            cmd('e',1)
            if e[5] == 3:
                time.sleep(2)
            else:
                time.sleep(0.5)



def monitor():
    command = ['w', 'nvidia-smi', 'last -n 10']
    time.sleep(randint(5,10))
    keyboard.press(Key.ctrl)
    time.sleep(0.5)
    keyboard.press(Key.tab)
    time.sleep(0.5)
    keyboard.release(Key.tab)
    time.sleep(0.5)
    keyboard.release(Key.ctrl)
    time.sleep(0.5)
    time.sleep(5)
    time.sleep(randint(2,30))
    cmd(command[randint(0, 2)], 5)
    time.sleep(20)

def watch_nodes():
    count = 0
    while True:
        count += 1
        if count > 9:
            count = 0
        if count == 1 or count == 2:
            time.sleep(5)
            continue
        else:
            monitor()

if __name__ == '__main__':
    # add_etf()
    watch_nodes()
    # change_root_passwd()
