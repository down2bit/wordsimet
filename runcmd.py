#!/usr/bin/env python3.0
## 08-July-2010, by Yuesheng Qi
## Update: from http to https

import socket, ssl
from time import sleep 
import sys,os

## constant variable defines
##import configuration_loader
##filepath = configuration_loader.ATE_Config.get("MAIN_PATH")+"/dongle/functional_suite/workspace/"
import config
filepath = config.get_main_dir()
#"/home/buildbot/dongle/functional_suite/workspace/"
global PrivateKeyFile, CertificateChainfile
PrivateKeyFile = os.path.join(filepath, 'privatekey.pem')
CertificateChainFile = os.path.join(filepath, 'certchain.pem')

HTTP_COMMAND_HEADER = ('POST / HTTP/1.1\r\n'
        + 'User-Agent: Morega PC Client\r\n'
        + 'Authorization: Basic YWRtaW5pc3RyYXRvcjphZG1pbmlzdHJhdG9y\r\n'
        + 'Pragma: no-cache\r\n'
        + 'Content-Type: application/x-www-form-urlencoded\r\n')

HTTP_COMMAND_CONTENT_LENGTH = "Content-Length: "

HTTP_COMMAND_HEADER_TERMINATOR = '\r\n'
python_version= sys.version[:3]

class ENUM_STATE :
    START = 0
    FIRSTR = 1
    FIRSTN = 2
    SECONDR = 3
    DONE = 4

MAX_HTTP_RETRY = 1

def skipHeaders(state, strbuf, ilen, strLog):

    if (state == ENUM_STATE.DONE) :
        return (ENUM_STATE.DONE, strbuf.decode('utf-8'), ilen, strLog)

    _data = ""
    _dataLen = 0

    _pos = 0
    _myS = state

    _bPrint = True
    for _pos in range (0,ilen):

        if _bPrint :
            if ("2.6" <= python_version):
                strLog = strLog + strbuf[_pos]
            else:
                strLog = strLog + chr(strbuf[_pos])
            
        if (strbuf[_pos] == '\r') :
                if (_myS == ENUM_STATE.START):
                    _myS = ENUM_STATE.FIRSTR
                else:    
                    if (_myS == ENUM_STATE.FIRSTN) :
                        _myS = ENUM_STATE.SECONDR
                    else :
                        _myS = ENUM_STATE.START

        else:
            if (strbuf[_pos] == '\n'):
                
                if (_myS == ENUM_STATE.FIRSTR):
                    _myS = ENUM_STATE.FIRSTN
                else:    
                    if (_myS == ENUM_STATE.SECONDR) :
                            _data = strbuf[_pos+1:]
                            _dataLen = ilen - _pos -1
                            _myS = ENUM_STATE.DONE
                            return (_myS, _data, _dataLen, strLog)
                    else :
                        _myS = ENUM_STATE.START
            else:
                _myS = ENUM_STATE.START;


    return (_myS, _data.decode('utf-8'), _dataLen, strLog)

def createSocketInput(strCommand, strParams, strLog):
    
    vpContentLengthNumStr = "%d" % (len(strCommand) )
    
    
    vpHeader = HTTP_COMMAND_HEADER
    vpContentLength = HTTP_COMMAND_CONTENT_LENGTH
    vpContentLength = vpContentLength + vpContentLengthNumStr

    strLog = strLog + ('OK\nWriting %d-byte commandHeader...' % len(vpHeader))
    strRet = vpHeader

    strLog = strLog + ( 'OK\nWriting %d-byte commandHeaderContentLength...' % len(vpContentLength))
    strRet = strRet + vpContentLength

##    // \r\n for Content-Length.
    strLog = strLog + ('OK\nWriting %d-byte commandHeaderTerminator...' % len(HTTP_COMMAND_HEADER_TERMINATOR))
    strRet = strRet + HTTP_COMMAND_HEADER_TERMINATOR

##    // \r\n for the whole header.
    strLog = strLog + ( 'OK\nWriting %d-byte commandHeaderTerminator...' % len(HTTP_COMMAND_HEADER_TERMINATOR))
    strRet = strRet + HTTP_COMMAND_HEADER_TERMINATOR

    strLog = strLog + ( 'OK\nWriting %d-byte command and para...' % len(strCommand))
    strRet = strRet + strCommand

#    strLog = strLog + ( 'OK\nWriting params separator...')
#    strRet = strRet + ":"

#    strLog = strLog + ( 'OK\nWriting parameters...')
#    strRet = strRet + strParams
    print ('cmd:"'+strCommand+'"')
    return (strRet, strLog)
    
def runCommand(sIP, iPort, strCommand, strParams =""):
    strLog = 'Testing command: %s \n' % strCommand
    strLog = strLog + 'Testing parameter: %s \n' % strParams
    strLog = strLog + "Creating socket..."

    i_tries =0
    b_connected = 0

    sleep (10)
    while ( i_tries < MAX_HTTP_RETRY):
#        print (i_tries)
        try:
            mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            b_connected =1
        except socket.error as e:
##            strLog = strLog + ('\nError creating socket: %s' % e )
            strLog = strLog + ('\nTry to create socket' )
            i_tries = i_tries +1
            b_connected = 0 
            print ("Try to create socket. " + str(i_tries)+"time(s)")
            sleep (2)

        strLog = strLog + ( 'OK\nConverting address...')
        strLog = strLog + ( 'OK\nConnecting to %s:%d...'% (sIP, iPort))
        #print PrivateKeyFile,CertificateChainFile
        if (1 == b_connected):
            try :
                _serversocket = ssl.wrap_socket(mysock,
                                            keyfile = PrivateKeyFile,
                                            certfile = CertificateChainFile,
                                            ssl_version = ssl.PROTOCOL_SSLv23 )
                print ("wrap_socket")
                _serversocket.connect((sIP, iPort))
            except ssl.SSLError as e:
                strLog = strLog + ( "\nSSL-related error : %s\n" % str(e))
                _serversocket.close()
                i_tries = i_tries +1
                print ("SSL-related error. Try again." + str(e) + str(i_tries)+"time(s)")
                sleep (2)
            except socket.gaierror as e:
                strLog = strLog + ( "\nGAI-related error : %s\n" % str(e))
                _serversocket.close()
                i_tries = i_tries +1
                print ("GAI-related error. Try again." + str(e) + str(i_tries)+"time(s)")
                sleep (2)
        
            except socket.error as e:
                strLog = strLog + ( "\nSocket error: %s\n" % str(e))
                _serversocket.close()
                i_tries = i_tries +1
                b_connected =0
                print (str(e) + "\nSocket error. Try again." + str(e) + str(i_tries)+"time(s)")
                sleep (2)

        if (1 == b_connected): break
  
    if (i_tries == MAX_HTTP_RETRY):
        strLog = strLog + ('\nError: Reached the Maximum Retry limitation' )
        #return strLog
        return "connection error"


   
    (strInput,strLog) = createSocketInput(strCommand, strParams, strLog)
    print ('cmd is:"'+strInput+'"')
    strLog = strLog + ( 'OK, %d bytes written\nReading response...' %len(strInput))
    _serversocket.send(strInput.encode("ascii"))
    msg4dongle=''
    myState = ENUM_STATE.START
    try:
        strRec= _serversocket.recv(4096)
    except socket.error as e:
        strLog = strLog + ( "\nConnection error: %s\n" % e)
        _serversocket.close()
        print ("HTTP connection error when recv data")
        return strLog

    while ( len(strRec) >0 ):
        (myState, strOut, iDataLen, strLog) = skipHeaders (myState, strRec, len(strRec), strLog)
        if (iDataLen >0) :
            msg4dongle +=strOut
            strLog = strLog + strOut
        strRec= _serversocket.recv(4096)

    _serversocket.close()

    return msg4dongle

def main(argv):
    if len(argv)<4:
        print ('Usage: python runcmd.py IP port command param')
        print ('Like: python runcmd.py 192.168.1.102 8082 ContentList') 
        print ('\n And privatekey.pem and certchain.pem must be in this folder.')
        return
    
    ip=argv[1]
    port=int(argv[2])
    cmd=argv[3]
    para=argv[4:] if (len(argv)>4) else ''
    
    global PrivateKeyFile
    PrivateKeyFile = './privatekey.pem'
    global CertificateChainFile
    CertificateChainFile = './certchain.pem'
    

    print (runCommand(ip, int(port), cmd, para))
        

##
##    TEST CODE
##    
    
if __name__ == "__main__":
    
    main(sys.argv)
    #print (runCommand("192.168.0.103",8082, "GetBlackList:"))
