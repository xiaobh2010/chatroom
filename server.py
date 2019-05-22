from socket import *
import sys
import os
import signal

#**************************************
def do_login(s,user,name,addr):
    for i in user:
        #定义的用户名重名，用户名是管理员时不添加进用户名字典
        if i==name or name=='管理员':
            s.sendto('FAIL'.encode(),addr)
            return
    s.sendto('OK'.encode(),addr)
    #新的用户登录时，该用户本身不会收到欢迎消息，是由于
    #新用户登录的地址信息还没有添加到用户字典中（下面进行遍历的时候）
    msg='\n欢迎%s进入聊天室'%name    
    for i in user:
        #发送给相应用户对应的地址
        s.sendto(msg.encode(),user[i])
    user[name]=addr
    return

#**************************************
def do_chat(s,user,tmp):
    msg='\n%-8s:%s'%(tmp[1],' '.join(tmp[2:]))
    #获取到的是字典的键值
    for i in user:
        if i!=tmp[1]:
            #发送消息给发送这者以外的所有用户
            s.sendto(msg.encode(),user[i])
    return 

#***************************************

def do_quit(s,user,name):
    #从用户字典删除该用户
    del user[name]
    msg='\n'+name+'离开了聊天室'
    #将用户退出消息告知其他用户
    for i in user:
        s.sendto(msg.encode(),user[i])
    return  

#***************************************
#踢人
def do_tiren(s,user,tmp):
    del user[tmp[3]]
    msg='\n'+tmp[3]+'被踢出聊天室'    
    for i in user:
        s.sendto(msg.encode(),user[i])
    return    

#接收处理
def do_child(s):
    # print('do child...')
    user={}
    while True:
        msg,addr=s.recvfrom(1024)
        msg=msg.decode()
        tmp=msg.split(' ')
        #以首字母来区分请求
        if tmp[0]=='L':
            do_login(s,user,tmp[1],addr)
        elif tmp[0]=='C':
            #'T 姓名'
            #踢出功能
            if tmp[2]=='T':
                do_tiren(s,user,tmp)
                return
            #有名字的话可以通过字典找到addr
            do_chat(s,user,tmp)            
        elif tmp[0]=='Q':
            do_quit(s,user,tmp[1])

        #调试用查看链接的客户端
        # print(user)

#发送系统消息,管理员发言
#发给自己，然后被do_child里面的recvfrom接收
#接收后执行do_chat给所有客户端发送信息
#父子进程同时占用终端
def do_parent(s,ADDR):
    name='C 管理员 '
    while True:
        msg=input('管理员消息：')
        msg=name+msg
        #先把消息发给服务器本身，再由服务器本身分发出去
        s.sendto(msg.encode(),ADDR)
    s.close()
    sys.exit(0)    

def main():
    if len(sys.argv)!=3:
        print('argv error')
        return 
    HOST=sys.argv[1]
    PORT=int(sys.argv[2])
    ADDR=(HOST,PORT)
    #创建数据保报套接字
    s=socket(AF_INET,SOCK_DGRAM)
    #当socket被关闭后，socket的端口号可以被立刻重用
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    #数据报套接字无连接
    #父进程不需要等待对子进程进行回收后才能退出，就不会形成孤儿进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    #创建进程
    pid=os.fork()
    if pid<0:
        print('create process failed')
        return
    elif pid==0:
        do_child(s)
    else:
        #管理员的消息发送
        do_parent(s,ADDR) 

if __name__=='__main__':
    main()
