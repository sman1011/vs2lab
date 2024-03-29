import threading
import time
import zipfile


class AsyncZip(threading.Thread):
    def __init__(self, infile, outfile):
        threading.Thread.__init__(self)
        self.infile = infile
        self.outfile = outfile

    def run(self):
        f = zipfile.ZipFile(self.outfile, 'w', zipfile.ZIP_DEFLATED)
        f.write(self.infile)
        f.close()
        time.sleep(5)  # pretend working
        print('Finished background zip of:', self.infile)


background = AsyncZip('mydata.txt', 'myarchive.zip')
background.start()
print('The main program continues to run in foreground.')
for i in range(0, 10):
    time.sleep(1)
    print("-" + str(i) + "-")
background.join()  # Wait for the background task to finish
print('Main program waited until background was done.')
