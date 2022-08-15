import os
import ntpath


def merge_files(daqdir, empdir, outdir=None):
    if outdir is None:
        outdir = os.path.join(os.path.dirname(daqdir), 'merged')
    if not os.path.exists(outdir):
        os.makedirs(outdirs)
    exe = ntpath.abspath('C:/Users/llafave/AppData/Roaming/EMP/DataMerge/DataMerge.exe')
    for test in os.listdir(daqdir):
        target = os.path.join(outdir, test+'.csv')
        if not os.path.exists(target):
            rename = re.compile(test+'.*')
            empfiles = [os.path.join(empdir, fname) for fname in os.listdir(empdir) if rename.match is not None]
            run([exe, os.path.join(daqdir, test), *empfiles], input=target, text=True)
