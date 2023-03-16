from json.tool import main
from pdb import runcall
import sys
import ssl
import socket
from tkinter.messagebox import YES


# function use for check if it support HTTP2 or not.
def SHTTP2(url):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context=ssl.SSLContext()
    context.set_alpn_protocols(['h2'])
    s=context.wrap_socket(s,server_hostname=url)
    s.connect((url,443))
    if s.selected_alpn_protocol()=="h2":
        return True
    else:
        return False


# connection function, it will first get a connect by port=80, if get 302 or 301, it will 
# check the location is https or http, if it is http, it will use that location as url and
# call connection again, if it is https, it will call connectionHTTPS.

def connection(url,path='/'):
    needpassword=0
    https=False
    port=80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((url,port))
    if (https==False):
        sendEncode="GET "+path+" HTTP/1.1"+"\r\nHost:"+url+"\r\n\r\n"
        sendEncode=sendEncode.encode()
        s.sendall(sendEncode)
        s.send(sendEncode)
        receive=s.recv(10000)
        receive=receive.decode().split("\n")
    else:
        connectionHTTPS(url)
    i=0
    
    # usefulR standfor useful receive, as we get such many receive but we only interesting in 
    # those informations before the blank, so I use usefulR to collect those massage to use.
    usefulR=[]
    while(i<len(receive)):
        usefulR.append(receive[i])
        if (receive[i]=="\r"):
            break
        i+=1

    # use cookie to collect cookie list.
    cookie=[]
    i=0
    https=False
    # for all things in usefulR, check if there is a 'Location', if have, means we get new webside
    # needs to get, split it to get that address and check it is https or http.
    while(i<len(usefulR)):
        if('Location'in usefulR[i]):
            newLocation_string="".join(usefulR[i])
            newLocation_string=newLocation_string.split(' ')
            url=newLocation_string[1]
            if('https'in url):
                connectionHTTPS(newLocation_string[1],path)
                https=True
            elif('http'in url):
                https=False
                url=url.split('/')
                url=url[2]
                connection(url)

        # check need password or not. 
        if('401'in usefulR[i]):
            needpassword=1

        # Set cookie list. 
        if('Set-Cookie:'in usefulR[i]):
            cookie.append(usefulR[i])
        if('400'in usefulR[0]):
            badrequest()
        i+=1   
    i=0

    # for here is because some time there is no 301 or 302, and it need to make sure 
    # something will not print twice. like print("2. List of Cookies:",end='')
    if('301' not in usefulR[0] and '302'not in usefulR[0]):
        print("2. List of Cookies:",end='')
        while(i<len(cookie)):
            cookie_sting="".join(cookie[i])
            cookie_list=cookie_sting.split(';')
            j=0
            while(j<len(cookie_list)):
                cookie_string2="".join(cookie_list)
                cookie_list2=cookie_string2.split("=")
                j+=1
            k=0
            while(k<len(cookie_list2)):
                
                if('Set-Cookie'in cookie_list2[k]):
                    a="".join(cookie_list2[k])
                    b=a.split(":")
               
                    print()
                    print("cookie name:",end='')
                    print(b[1],end='')
                   
                if('expires'in cookie_list2[k]):
                    print("; expire time:",end='')
                    print(cookie_list2[k+1],end='')
                   
                if('domain'in cookie_list2[k]):
                    str="".join(cookie_list2[k+1])
                    domainName=str.split(" ")

                    print("; domain name:",end='')
                    print(domainName[0],end="")
                    
                k+=1
            i+=1
        if(needpassword==0):
            print()
            print("3. Password-protected: no")
        else:
            print()
            print("3. Password-protected: yes")
        s.close     
    return


def badrequest():
    print("Bad request, 400")
    
    return True 

# function for HTTPS, almost same like connection, but for https.
def connectionHTTPS(url,path='/'):
    needpassword=0
   
    https=False
    
    port = 443
    if('https'in url):
        https=True
        url=url.split('/')     
        url=url[2]  
    if https:    
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # create a new socket with http/1.1
        context.set_alpn_protocols(["http/1.1"])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = context.wrap_socket(s, server_hostname=url)
    else:
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print(url)
    s.connect((url, port))
    a="GET " + path + " " + "HTTP/1.1"  + "\r\nHost: " + url + "\r\n\r\n"
    a=a.encode()
    s.sendall(a)
    response = s.recv(10000)
    response=response.decode().split("\n")
    i=0
    usefulR=[]
    while(i<len(response)):
        usefulR.append(response[i])
        if (response[i]=="\r"):
            break
        i+=1
    cookie=[]
    i=0
    while(i<len(usefulR)):
        if('Location'in usefulR[i]):
            newLocation_string="".join(usefulR[i])
            newLocation_string=newLocation_string.split(' ')
            url=newLocation_string[1]
            if('https'in url):
                https=True
                url=url.split('/')
                url=url[2]
                connectionHTTPS(newLocation_string[1])
        if('401'in usefulR[0]):
            needpassword=1
        if('400'in usefulR[0]):
            badrequest()
        if('Set-Cookie:'in usefulR[i]):
            cookie.append(usefulR[i])      
        i+=1
    i=0
    if('301' not in usefulR[0] and '302'not in usefulR[0]):
        print("2. List of Cookies:",end='')
        while(i<len(cookie)):
            cookie_sting="".join(cookie[i])
            cookie_list=cookie_sting.split(';')
            j=0
            while(j<len(cookie_list)):
                cookie_string2="".join(cookie_list)
                cookie_list2=cookie_string2.split("=")
                j+=1
            k=0
            while(k<len(cookie_list2)):
                
                if('Set-Cookie'in cookie_list2[k]):
                    a="".join(cookie_list2[k])
                    b=a.split(":") 
                    print()
                    print("cookie name:",end='')
                    print(b[1],end='')      
                if('expires'in cookie_list2[k]):
                    print("; expire time:",end='')
                    print(cookie_list2[k+1],end='')
                if('domain'in cookie_list2[k]):
                    str="".join(cookie_list2[k+1])
                    domainName=str.split(" ")       
                    print("; domain name:",end='')
                    print(domainName[0],end="")           
                k+=1
            i+=1
        if(needpassword==0):
            print()
            print("3. Password-protected: no")
        else:
            print()
            print("3. Password-protected: yes")
        s.close  
    return


# use for check the user's input, if it can get connected, I think it 
# should be a webside if yes, it will return 1, if not it will return None. 
def checkurl(url):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((url,80))
    except:
        return None
    return 1


# main function
def main():
    path='/'
    # ask for input, if input have /, it will set the things after/ to be path.
    print("please enter a webside")
    url=input()
    if("/"in url):
        ls=url.split("/",1)
        url=ls[0]
        path='/'+ls[1]
    
    
    curl=checkurl(url)
    
    # check if the user enter a webside.
    while(curl==None):
        print("You enter something which is not a webside or something wrong, please check if it correct webside or use ctrl+c to end")
        url=input()
        curl=checkurl(url)

    # The first thing need to print as output.
    print("website: "+url) 
    
    # check if it support HTTP2
    supportHttp2=SHTTP2(url)
    
    # The second thing need to print as output.
    if(supportHttp2==True):
        print("1. Supports http2: yes")
    if(supportHttp2==False):
        print("1. Supports http2: no")
    
    # Get Connection 
    connection(url,path)




if __name__ == "__main__":
    main()
	
    