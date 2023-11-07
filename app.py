#!/usr/bin/env python
# coding: utf-8

# In[1]:


try:
    if __file__ != '__main__.py': 
        debug = False
except: 
    debug = True
    get_ipython().system('jupyter nbconvert --to script __main__.ipynb')
    get_ipython().system('del app.py')
    get_ipython().system('move __main__.py app.py')


# In[ ]:


import time , datetime
_ScriptStartAt = time.time()
now = lambda:datetime.datetime.now().strftime("%Y%m%d%H%M%S_%f")


# In[ ]:


config = {
    "STORAGE":"."   # WHERE ALL HASH FILES GONNA BE SAVED
    # "STORAGE":"\\\\?\\Volume{17b24389-ad3f-48b8-b5bd-553b6a38e726}\\STORAGE", # WHERE ALL HASH FILES GONNA BE SAVED
    # "INDEX.db":"W:/STORAGE/index.sqlite3" # WHERE ALL HISTORY WILL BE REMEMBERED IN SHITSTORM SHITSHOW CRAP HAPPENS
} 


# In[ ]:


def spawn2stdout(cmd):
    if type(cmd) == bytes:
        cmd = cmd.decode()
    
    import subprocess,sys
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout=bytes()
    stderr=bytes()

    while process.poll() == None or len(out) != 0:
        out = process.stdout.readline(1)
        stdout += out
        out = process.stderr.readline(1)
        stderr += out
    return stdout , stderr


# In[ ]:


import zlib

class crc32(object):
    name = 'crc32'
    digest_size = 4
    block_size = 1

    def __init__(self):
        self.__digest = 0

    def digest(self):
        return list((self.__digest).to_bytes(4, byteorder='big'))

    # def digest(self):
    #     # return '{:08x}'.format(self.__digest)
    #     return list(self.__digest.to_bytes(4, byteorder='big'))

    def update(self, arg):
        self.__digest = zlib.crc32(arg, self.__digest) & 0xffffffff

# Now you can define hashlib.crc32 = crc32
import hashlib
hashlib.crc32 = crc32


# In[ ]:


def trycatch(func,errfunc):
    try:
        return func()
    except Exception as e:
        if errfunc:
            return errfunc(e)
        return e


# In[ ]:


def hash_file(filename,tempDir=config["STORAGE"] + "\\temp\\"):
    import os, os.path as path
    assert path.isfile(filename) , "File not found for hash operation"

    class length():
        def __init__(self):
            self.size=0
        def update(self,data):
            self.size+=len(data)
        def digest(self):
            return list(self.size.to_bytes(8, byteorder='big'))

    class sumAll():
        def __init__(self):
            self.size=0
        def update(self,data):
            self.size+=sum(list(data))
        def digest(self):
            return list(self.size.to_bytes(10, byteorder='big'))

    class copyFile():
        def __init__(self):
            try:
                if tempDir is None: return
                import datetime
                import random
                # currentDT = datetime.datetime.now()
                # self.fname =  "f:\\temp\\" + currentDT.strftime("%Y%m%d%H%M%S_%f_")+str( random.randint(0,99999) ).zfill(5)+'.tmp'
                self.fname =  tempDir + datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f_")+str( random.randint(0,99999) ).zfill(5)+'.tmp'
                os.makedirs( os.path.dirname( self.fname ) ,exist_ok=True )
                self.fopen = open(self.fname , "wb" )
            except:
                self.fopen.close()
                raise Exception(self.fname," Path Cannot be written. ")
        def update(self,data):
            if tempDir is None: return
            try:
                self.fopen.write(data)
            except:
                self.fopen.close()
                raise
            None
        def digest(self):
            if tempDir is None: return
            self.fopen.close()
            return self.fname

    hashes = [ #### make a hash object

        # [ 'blake2b' , hashlib.blake2b() ],
        # [ 'blake2s' , hashlib.blake2s() ],
        # [ 'sha224' , hashlib.sha224() ],
        # [ 'sha384' , hashlib.sha384() ],
        # [ 'sha3_224' , hashlib.sha3_224() ],
        # [ 'sha3_256' , hashlib.sha3_256() ],
        # [ 'sha3_384' , hashlib.sha3_384() ],
        # [ 'sha3_512' , hashlib.sha3_512() ],
        # [ 'sha512' , hashlib.sha512() ],
        # [ 'shake_128' , hashlib.shake_128() ],
        # [ 'shake_256' , hashlib.shake_256() ],
        [ 'crc32' , hashlib.crc32() ] ,
        [ 'md5' , hashlib.md5() ] ,
        [ 'sha1' , hashlib.sha1() ] ,
        [ 'sha256' , hashlib.sha256() ] ,
        [ "sumAll" , sumAll() ] ,
        [ "length" , length() ] ,
        [ "copyFPath" , copyFile() ],

    ]

    with open(filename,'rb') as file:   ### open file for reading in binary mode
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024*4 )  ### read file in chunks and update hash
            # h_sha256.update(chunk) ### old code. below there is a new way to do this
            for _,hash2 in hashes:
                hash2.update( chunk )

    hashResult = []
    for hashName , hashFunc in hashes:  ### return the hex digest of each hash engine
        tmp = hashFunc.digest()
        try:
            hashResult.append( [ hashName , "".join([ ("0"+hex(x)[2:])[-2:] for x in list( tmp ) ] ) ] ) ### convert to hex
        except:
            hashResult.append( [ hashName , tmp ] ) ### save as it is
    return hashResult


# In[ ]:


import re,os
def getAllDisksMount():
    # disksList = re.findall(r"(\\\\?\\.*\{[0-9a-f]{8}-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}\}\\)",os.popen("mountvol").read(),re.MULTILINE) ## "wmic VOLUME get DeviceID"
    disksList = re.findall(r"(\\\\?\\.*\{[0-9a-f]{8}-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}\}\\)",os.popen("wmic VOLUME get DeviceID").read(),re.MULTILINE)
    letters = [ chr(x) + ":\\" for x in range(65,90) if os.path.exists( chr(x) + ":\\" ) ]

    for vol , letter in re.findall(r"(\\\\?\\.*\{[0-9a-f]{8}-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}\}\\)\n\s+(.*)",os.popen("mountvol").read(),re.MULTILINE):
        try:
            if vol in disksList:
                letters.remove( letter[:2]+"\\" )
        except: None

    for letter in re.findall(r"\nOK\s+([a-zA-Z]:)\s+\\\\.+?\s+Microsoft Windows Network" , os.popen("net use").read() ):
        letters.remove(letter+"\\")

    return disksList + letters
getAllDisksMount()


# In[ ]:


def listdir(path):
    try: tmp = [ os.path.join(path,x) for x in os.listdir(path) ] 
    except: tmp = []
    tmp.sort()
    return tmp
# listdir = lambda path:[ os.path.join(path,x) for x in os.listdir(path) ] 

def walkdir(path):
    paths = [ path ]
    while len(paths) > 0:

        path = paths.pop(0)

        if path.lower() == "SHA256_SHA1_MD5".lower():
            continue
        
        try:
            os.readlink(path)
            yield path
            continue
        except:
            None

        try:
            if os.path.isdir(path):
                if os.path.basename(path).lower() in [ path_x.lower() for path_x in ["DUMP","Sysmon",".ipynb_checkpoints","CacheManager","Steamlibrary","htmlcache","SteamApps","log","temp","tmp","STORAGE","AppCache","cacho","raw","morgue","Cache","cache2","Caches","Code Cache","CacheStorage","Code","D3DSCache","GPUCache","GrShaderCache","INetCache","jumpListCache","optimization_guide_hint_cache_store","ScriptCache","shader-cache","ShaderCache","shadercache","startupCache","$RECYCLE.BIN","System Volume Information","Temporary Internet Files"] ]:
                    continue
                paths = [ os.path.join(path,x) for x in os.listdir(path) ] + paths
                continue
            else:
                tmp = path.lower()
                if True in [ tmp.endswith( ext.lower() ) for ext in [ ".STORAGETHIS" , ".tmp" , ".temp" , ".log" , ".ztmp" , ".evt" , ".evtx" , ".dmp" , ".dump"  , ".etl" ] ]:
                    continue
                yield path
        except KeyboardInterrupt:
            raise
        except:
            None

def walkdirs(path):
    assert type(path) == list, "Expected 'list' "

    paths = [ walkdir(x) for x in path ]
    x = 0
    while True:
        try:
            yield next( paths[x] )
        except KeyboardInterrupt:
            raise
        except StopIteration:
            paths.remove( paths[x] )
            x+=-1
        except:
            if len( paths ) == 0:
                return
            paths.pop(x)
            x+=-1
        x+=1
        if x >= len( paths ):
            x=0


# In[ ]:


listaArquivos = set()


# In[ ]:


def __Worker_Backup():
    import random , datetime

    fNameBkp = "Mapping_" + str(_ScriptStartAt) + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S_%f_") + str( random.randint(0,99999) ).zfill(5) + ".csv"
    with open( config["STORAGE"] + "\\"+ fNameBkp,"ab" ) as f_io:
        filehashed_Count=1
        while filehashed_Count !=0: ### in case no files are found, stop the script
            filehashed_Count=0
            try:
                for filePath in walkdirs( getAllDisksMount() ) :
                    sha256,sha1,md5,stat = None,None,None,None
                    try:
                        if "\\temp\\"   in  filePath :
                            continue
                        if "/temp/"     in  filePath :
                            continue
                        stat = os.stat( filePath )
                        fileStats = [ [ "n_fields" , stat.n_fields ] ,[ "n_sequence_fields" , stat.n_sequence_fields ] ,[ "n_unnamed_fields" , stat.n_unnamed_fields ] ,[ "st_atime" , stat.st_atime ] ,[ "st_atime_ns" , stat.st_atime_ns ] ,[ "st_ctime" , stat.st_ctime ] ,[ "st_ctime_ns" , stat.st_ctime_ns ] ,[ "st_dev" , stat.st_dev ] ,[ "st_file_attributes" , stat.st_file_attributes ] ,[ "st_gid" , stat.st_gid ] ,[ "st_ino" , stat.st_ino ] ,[ "st_mode" , stat.st_mode ] ,[ "st_mtime" , stat.st_mtime ] ,[ "st_mtime_ns" , stat.st_mtime_ns ] ,[ "st_nlink" , stat.st_nlink ] ,[ "st_reparse_tag" , stat.st_reparse_tag ] ,[ "st_size" , stat.st_size ] ,[ "st_uid" , stat.st_uid ] ]
                        fileSize = stat.st_size
                        if ( filePath + str(stat.st_ctime_ns) + str(stat.st_mtime_ns) ) in listaArquivos:
                            continue

                        ### All Green, lets hash the file, then copy it to the backup folder
                        
                        message = hash_file( filePath )# , tempDir="T:\\STORAGE\\TEMP\\" )
                        tmp = [ [ "filePath" , filePath ] ] + message + [ [ "scriptStart" , _ScriptStartAt ],[ "hashTimeAt" , time.time() ] ] + fileStats

                        f_io.write( "*".join( [ str( x[1] ) for x in tmp ] ).encode() )
                        f_io.write( "\r\n".encode() )

                        for varName , Val in message:
                            if varName == "md5": md5 = Val
                            if varName == "sha1": sha1 = Val
                            if varName == "sha256": sha256 = Val
                            if varName == "copyFPath": copyFPath = Val

                        temporarily = copyFPath
                        StoragePath = os.path.join( config["STORAGE"] , "SHA256_SHA1_MD5" , sha256[0:2] , sha256[2:4] , sha256 + "_" + sha1 + "_" + md5  )

                        os.makedirs( os.path.dirname( StoragePath ) , exist_ok=True )                        
                        trycatch( lambda: spawn2stdout( 'cmd /c move "'+temporarily+'" "'+StoragePath+'" ' ) )

                        try:    listaArquivos.add( ( filePath + str(stat.st_ctime_ns) + str(stat.st_mtime_ns) ) )
                        except: listaArquivos.append( ( filePath + str(stat.st_ctime_ns) + str(stat.st_mtime_ns) ) )


                        filehashed_Count+=1 ### tell the script that at least one file was hashed

                    except KeyboardInterrupt as Keyb:
                        raise
                    except Exception as Err:
                        if Err.args in [
                            ('File not found for hash operation',),
                            
                            (2 , 'The system cannot find the path specified'),
                            (2 , 'The system cannot find the file specified'),
                            (2 , 'The network path was not found'),
                            
                            (13, 'Permission denied'),
                            (13, 'Access is denied'),
                            (13, 'The device is not ready'),
                            
                            (22, 'Invalid argument'),
                            (22, 'A device which does not exist was specified'),
                            (22, 'The file cannot be accessed by the system'),
                            (22, 'The symbolic link cannot be followed because its type is disabled'),
                            (22, 'An unexpected network error occurred'),
                            (22, 'The semaphore timeout period has expired'),                            
                        ]:
                            continue

            except KeyboardInterrupt as Keyb:
                raise
            except StopIteration:
                continue
            except:
                None


# In[ ]:


thread1 = None
def __Worker_Backup_START():
    global thread1
    try:
        if not thread1.is_alive():
            raise 0
        # print(" Thread is \033[96m ALREADY \033[1;0m Running")
        return '{"result":"RunningAlready"}'
    except:
        from threading import Thread
        thread1 = Thread( target=__Worker_Backup , args=() )
        thread1.start()
        # print(" Thread has \033[95m STARTED \033[1;0m Running")
        return '{"result":"OK"}'


# In[ ]:


__Worker_Backup_START()


# In[ ]:


# https://htmx.org/examples/
# flask


# In[ ]:


if debug:
    get_ipython().run_line_magic('pip', 'install flask')


# In[ ]:


import os


# In[ ]:


from flask import Flask , Response , redirect
if debug:
    app = Flask("")#__name__)
else:
    app = Flask(__name__)

@app.route('/')
def hello():
    return redirect("/index.html", code=302)

get_resource = lambda *argp:"<html><head/><body/></html>"
@app.route('/<path:path>')
def __get_resource( path ):  # pragma: no cover
    global get_resource
    return get_resource( path )

@app.route('/api/v0/status')
def __status():  # pragma: no cover
    global status
    return status

@app.route('/api/v0/startBackup')
def __Worker_Backup_Status( ):  # pragma: no cover
    global __Worker_Backup_START
    return __Worker_Backup_START()

app.debug = True
__main__ = lambda: app.run( host='127.0.0.1' , port=18080 , debug=True )

if debug:
    from threading import Thread
    Thread( target=__main__, args=() ).start()


# In[ ]:


def get_resource( path ):  # pragma: no cover
    print("###" , path )
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    if os.path.exists( path ):
        with open( path ) as f_io:
            return Response( f_io.read() , mimetype=mimetypes.get( path.split(".")[-1] , "text/html") )
    else:
        return Response( status=404 )


# In[ ]:


# @app.root()
# def __HTMLRoot__(ur):
    # with open("index.html") as f_io:
        # return f_io.read()


# In[ ]:


def HTMLRoot():
    with open("index.html") as f_io:
        return f_io.read()


# In[ ]:


HTMLRoot()

