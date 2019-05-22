from socket import *
import sys
import os
import signal

#发送请求
def do_child(s,addr,name):
    while True:
        text=input('发言:')
        if text=='quit':
            #本身是无连接的通讯，不加上姓名的话不知道谁退出了
            msg='Q '+name
            s.sendto(msg.encode(),addr)
            #父进程先退出子进程就变成孤儿进程了
            #没有必要在父进程中忽略子进程
            #父子进程都退出了客户端也就自动退出了
            os.kill(os.getppid(),signal.SIGKILL)
            sys.exit(0) 
        #正常聊天
        else:
            msg='C %s %s'%(name,text) 
            s.sendto(msg.encode(),addr)  

#接收服务器中遍历字典得到的信息
def do_parent(s):
    while True:
        msg,addr=s.recvfrom(1024)
        print(msg.decode()+'\n发言：',end='')

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
    #
    #－－－－－－－－用户登录－－－－－－－－
    while True:
        name=input('请输入姓名:')
        msg='L '+name
        #从哪里发送的
        s.sendto(msg.encode(),ADDR)
        #接收来自哪里的消息
        data,addr=s.recvfrom(1024)
        if data.decode()=='OK':
            break
        else:
            print('用户名已存在')
            
    #－－－－－－－－－－－－－－－－－－－－
    #        
    # signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    #创建进程
    pid=os.fork()
    if pid<0:
        print('create process failed')
        return
    elif pid==0:
        do_child(s,addr,name)
    else:
        do_parent(s)

if __name__=='__main__':
    main()
