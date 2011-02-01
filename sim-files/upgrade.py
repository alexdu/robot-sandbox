import os
import urllib
import time
import zipfile
import shutil
import sys
import subprocess


print
print "robot-sandbox upgrade"
print "====================="
print "This will also delete all your robot programs. "

ans = ""
while 1:
    ans = raw_input("Are you sure? [yes/no] ")
    if ans in ['yes', 'no']:
        break
    print "Please answer 'yes' or 'no'."
    

def unzip(file, dir):
    if os.path.isdir(dir):
        rmrf(dir)
    os.mkdir(dir)
    zfobj = zipfile.ZipFile(file)
    mainfolder = zfobj.namelist()[0][:-1]
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
    return mainfolder


def rmrf(folder, exc = False):
    if sys.platform == "win32":
        rm = "rmdir /s /q "
    else:
        rm = "rm -rf "

    ret = os.system(rm + folder)
    if exc:
        if ret != 0: 
            raise Exception, "error deleting " + folder



lastp = 0
def progress(a,b,c):
    global lastp
    p = int(a * b * 100.0 / c)
    if p > lastp:
        print '%s\r' % ' ' * 20, 
        print '%d%%' % p, 
        lastp = p

if ans == "yes":
    try:
        print time.time()

        os.chdir("..")
        print os.getcwd()

        url = "http://github.com/alexdu/robot-sandbox/zipball/master"
        
        print "downloading ", url, " ..."
        urllib.urlretrieve(url, "temp.zip", progress)
        print ""
        print "unzip..."

        mainfolder = unzip("temp.zip", "upgradetmp")

        if sys.platform == "win32":
            upgbat = os.path.join("upgradetmp", "upgrade.bat")
            f = open(upgbat, "wt")
            f.write("ping -n 2 127.0.0.1 >NUL \n") # pe post de delay :)
            f.write('del /f /q "%s" \n' % os.getcwd())
            for folder in ["robot-programs", "sim-files", "libs"]:
                f.write('rmdir /s /q "%s" \n' % os.path.join(os.getcwd(), folder))
            f.write('xcopy /e /y /r "%s" "%s" \n' % (os.path.join(os.getcwd(), "upgradetmp", mainfolder, "*.*"), 
                                                os.getcwd() + "\\" ))
            f.write('rmdir /s /q "%s" \n' % os.path.join(os.getcwd(), "upgradetmp", mainfolder))
            f.write("pause \n")
            f.close()
            print "harakiri..."
            
            subprocess.Popen(upgbat)
            os.abort()
        else:
            print "cleanup..."
            for folder in ["robot-programs", "sim-files", "libs"]:
                rmrf(folder)

            print "copying new files..."
            ret = os.system("cp -fr %s ." % (os.path.join("upgradetmp", mainfolder, "*")))
            if ret != 0: raise Exception, "error copying new files"
            print "cleaning temporary folders..."
            shutil.rmtree("upgradetmp", False)
            os.remove("temp.zip")
            print "Upgrade complete"
            raw_input("Press ENTER to continue... ")
            os.abort()    
    except Exception:
        #traceback.print_tb(sys.last_traceback)
        print ""
        print "Upgrade FAILED. Please download the program again. Sorry for trouble..."        
        print ""
        raw_input("Press ENTER to continue... ")
        os.abort()    
        #raw_input("Please restart the program. ")
        #raw_input("Press ENTER to continue... ")
        #os.abort()    
    
