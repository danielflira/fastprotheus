#!/usr/bin/python

import logging, zipfile, tarfile, re, os, stat, shutil, argparse, subprocess

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


def copy2_safe(origpath, targpath):
    if os.path.islink(origpath):
        linkto = os.readlink(origpath)
        os.symlink(linkto, targpath)
    else:
        os.chmod(origpath, stat.S_IWRITE)
        shutil.copy2(origpath, targpath)


def move_safe(origpath, targpath):
    if os.path.islink(origpath):
        linkto = os.readlink(origpath)
        os.symlink(linkto, targpath)
        os.remove(origpath)
    elif os.path.isdir(origpath):
        os.chmod(origpath, stat.S_IWRITE)
        os.rename(origpath, targpath)
    else:
        os.chmod(origpath, stat.S_IWRITE)
        shutil.copy2(origpath, targpath)
        os.remove(origpath)


def makedirs_safe(dirpath):
    dirpath2 = os.path.dirname(dirpath)
    if dirpath == dirpath2:
        return
    makedirs_safe(dirpath2)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)


def rmdir_safe(dirpath):
    if not os.path.exists(dirpath):
        return
    for dirname in os.listdir(dirpath):
        rmdir_safe(os.path.join(dirpath, dirname))
    os.rmdir(dirpath)


def rename_safe(sourcepath, targetpath):
    if not os.path.islink(sourcepath):
        os.chmod(sourcepath, stat.S_IWRITE)
    move_safe(sourcepath, targetpath)


def remove_safe(sourcepath):
    if not os.path.islink(sourcepath):
        os.chmod(sourcepath, stat.S_IWRITE)
    os.remove(sourcepath)


def move_dir_with_replace(dirpath, dirtarget):
    # backup current dir
    here = os.getcwd()
    try:
        # move file
        os.chdir(dirpath)
        for path, dirs, files in os.walk('.'):
            for file in files:
                origpath = os.path.join(path, file)
                targpath = os.path.join(dirtarget, path, file)
                if os.path.exists(targpath):
                    remove_safe(targpath)
                makedirs_safe(os.path.dirname(targpath))
                rename_safe(origpath, targpath)
        os.chdir(here)
        return True
    except:
        os.chdir(here)
        return False


def copy_dir_with_replace(dirpath, dirtarget):
    # backup current dir
    here = os.getcwd()
    try:
        # move file
        os.chdir(dirpath)
        for path, dirs, files in os.walk('.'):
            for file in files:
                origpath = os.path.join(path, file)
                targpath = os.path.join(dirtarget, path, file)
                if os.path.exists(targpath):
                    remove_safe(targpath)
                makedirs_safe(os.path.dirname(targpath))
                copy2_safe(origpath, targpath)
        os.chdir(here)
        return True
    except:
        os.chdir(here)
        return False


def copy_file_with_replace(filepath, filetarg):
    dirtarg = os.path.dirname(filetarg)
    if os.path.exists(filetarg):
        remove_safe(filetarg)
    makedirs_safe(dirtarg)
    copy2_safe(filepath, filetarg)


def remove_files(dirpath):
    for path, dirs, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(path, filename)
            remove_safe(filepath)
    rmdir_safe(dirpath)


def unzip_with_replace(filepath, target):
    zfp = zipfile.ZipFile(filepath, mode='r')
    zfp.extractall(target)
    zfp.close()


def unzip_with_replace_safe(filepath, target):
    try:
        unzip_with_replace(filepath, target)
        return True
    except:
        logging.debug('{0} nao eh um zip'.format(filepath))
        return False


def untar_with_replace(filepath, target):
    tfp = tarfile.open(filepath, mode='r')
    tfp.extractall(target)
    tfp.close()


def untar_with_replace_safe(filepath, target):
    try:
        untar_with_replace(filepath, target)
        return True
    except:
        logging.debug('{0} nao eh um tar'.format(filepath))
        return False


def uncompress(filepath, target):
    if not unzip_with_replace_safe(filepath, target):
        if not untar_with_replace_safe(filepath, target):
            return False
    return True


def unpack_all_files(dirname):
    for path, dirs, files in os.walk(dirname):
        for file in files:
            filepath = os.path.join(path, file)
            extension = os.path.splitext(file)[1].lower()
            if extension in ['.zip', '.gz', '.bz2', '.z']:
                if uncompress(filepath, path):
                    remove_safe(filepath)
                else:
                    return False
    return True


'''
dbaccess install process for linux
'''

def prepare_linux_dbaccess(filepath, workdir):
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    logging.info("preparando ({0})".format(filename))

    # unpack files and subfiles
    uncompress(filepath, workdir)
    unpack_all_files(workdir)


def install_linux_dbaccess(workdir, instdir):
    targdir = os.path.join(instdir, 'dbaccess')
    logging.info("instalando dbaccess")

    # fix: test result
    move_dir_with_replace(workdir, targdir)


'''
protheus binary install process for linux
'''

def prepare_linux_binario(filepath, workdir):
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    logging.info("preparando ({0})".format(filename))

    # unpack files and subfiles
    unzip_with_replace(filepath, workdir)
    
    # duas passadas que tem bastante coisa...
    unpack_all_files(workdir)
    unpack_all_files(workdir)

    # rename smartclient
    oname = os.path.join(workdir, 'smartclientLinux')
    tname = os.path.join(workdir, 'smartclient')
    rename_safe(oname, tname)

    # rename appserver
    oname = os.path.join(workdir, 'appserverLinux')
    tname = os.path.join(workdir, 'appserver')
    rename_safe(oname, tname)

    # appserver dir
    appserverdir = tname

    # rename appserver binary
    oname = os.path.join(appserverdir, 'appsrvlinux')
    tname = os.path.join(appserverdir, 'appserver')
    rename_safe(oname, tname)

    # verifica maior ace
    acepath = ''
    for path, dirs, files in os.walk(appserverdir):
        for dirname in dirs:
            if dirname.startswith('ace_'):
                if dirname > acepath:
                    acepath = dirname
    acepath = os.path.join(appserverdir, acepath)
    copy_dir_with_replace(acepath, '..')


def install_linux_binario(workdir, instdir):
    targdir = os.path.join(instdir, 'bin')
    logging.info("instalando binario")

    # fix: test result
    move_dir_with_replace(workdir, targdir)


'''
protheus dictionary install process
'''

def prepare_dicionario(filepath, workdir):
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    logging.info("preparando ({0})".format(filename))

    unzip_with_replace(filepath, workdir)

    systemload = os.path.join(workdir, 'systemload')
    move_dir_with_replace(workdir, systemload)


def install_dicionario(workdir, instdir):
    targdir = os.path.join(instdir, 'protheus_data')
    logging.info("instalando dicionario")

    # fix: test result
    move_dir_with_replace(workdir, targdir)


'''
protheus dictionary install process
'''

def prepare_help(filepath, workdir):
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    logging.info("preparando ({0})".format(filename))

    unzip_with_replace(filepath, workdir)

    bra = os.path.join(workdir, 'bra')
    systemload = os.path.join(workdir, 'systemload')
    
    move_dir_with_replace(bra, systemload)
    remove_files(bra)


def install_help(workdir, instdir):
    targdir = os.path.join(instdir, 'protheus_data')
    logging.info("instalando helps")

    # fix: test result
    move_dir_with_replace(workdir, targdir)


'''
protheus menu install process
'''

def prepare_menu(filepath, workdir):
    dirpath = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    logging.info("preparando ({0})".format(filename))

    unzip_with_replace(filepath, workdir)

    system = os.path.join(workdir, 'system')
    move_dir_with_replace(workdir, system)



def install_menu(workdir, instdir):
    targdir = os.path.join(instdir, 'protheus_data')
    logging.info("instalando menus")

    # fix: test result
    move_dir_with_replace(workdir, targdir)


'''
protheus system directory move
'''

def move_to_system(filepath, instdir):
    filename = os.path.basename(filepath)
    targfile = os.path.join(instdir, 'protheus_data', 'system', filename)
    copy_file_with_replace(filepath, targfile)


'''
protheus apo directory move
'''

def move_to_apo(filepath, instdir):
    filename = os.path.basename(filepath).split('-')[-1].lower()
    targfile = os.path.join(instdir, 'apo', filename)
    copy_file_with_replace(filepath, targfile)

    # check rpo version
    versao = re.search('(\d+).rpo', filename, re.I).groups()
    if len(versao) > 0:
        print('export RPOVERSION={0}'.format(versao[0]))


'''
identify package to install and start install process
'''

def install_package(workdir, instdir, filepath):
    filename = os.path.basename(filepath)

    if re.match('.+dbaccess.+linux', filepath, re.I):
        logging.info("dbaccess linux ({0})".format(filename))
        prepare_linux_dbaccess(filepath, workdir)
        install_linux_dbaccess(workdir, instdir)
        remove_files(workdir)

    if re.match('.+binario.+linux', filepath, re.I):
        logging.info("binario linux ({0})".format(filename))
        prepare_linux_binario(filepath, workdir)
        install_linux_binario(workdir, instdir)
        remove_files(workdir)
    
    if re.match('.+dicionarios', filepath, re.I):
        logging.info("dicionario ({0})".format(filename))
        prepare_dicionario(filepath, workdir)
        install_dicionario(workdir, instdir)
        remove_files(workdir)
    
    if re.match('.+bra.+helps', filepath, re.I):
        logging.info("helps ({0})".format(filename))
        prepare_help(filepath, workdir)
        install_help(workdir, instdir)
        remove_files(workdir)

    if re.match('.+bra.+menus', filepath, re.I):
        logging.info("menus ({0})".format(filename))
        prepare_menu(filepath, workdir)
        install_menu(workdir, instdir)
        remove_files(workdir)

    if re.match('.+ttt.+rpo$', filepath, re.I):
        logging.info("repositorio ({0})".format(filename))
        move_to_apo(filepath, instdir)

    if re.match('.+sigaadv.pss', filepath, re.I):
        logging.info("arquivo ({0})".format(filename))
        move_to_system(filepath, instdir)

    if re.match('.+sigapss.spf', filepath, re.I):
        logging.info("arquivo ({0})".format(filename))
        move_to_system(filepath, instdir)


def scan_install_package(args):
    workdir = '/tmp/workdir/'
    instdir = '/protheus/'

    for path, dirs, files in os.walk('./packages'):
        for file in files:
            filepath = os.path.join(path, file)
            install_package(workdir, instdir, filepath)


def run_dbaccess():
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename == 'dbaccess':
                # inicia o servico
                newenv = os.environ.copy()
                newenv['PATH'] += ':' + os.path.abspath(root)
                newenv['LD_LIBRARY_PATH'] = os.path.abspath(root)
                while True:
                    proc = subprocess.Popen([filename], env=newenv, cwd=root)
                    proc.wait()
                    print('{0} executando'.format(filename))


def run_appserver():
    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename == 'appserver':
                # inicia o servico
                newenv = os.environ.copy()
                newenv['PATH'] += ':' + os.path.abspath(root)
                newenv['LD_LIBRARY_PATH'] = os.path.abspath(root)
                while True:
                    proc = subprocess.Popen([filename], env=newenv, cwd=root)
                    proc.wait()
                    print('{0} executando'.format(filename))


def main(args):
    if args.install:
        scan_install_package(args)
    if args.start_dbaccess:
        run_dbaccess()
    if args.start_appserver:
        run_appserver()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configurar protheus')

    parser.add_argument('--install', action='store_true', default=False,
            help='instala os pacotes que estao no diretorio')
    parser.add_argument('--start-dbaccess', action='store_true', default=False,
            help='inicializa o dbaccess no ambiente')
    parser.add_argument('--start-appserver', action='store_true', default=False,
            help='inicializa o appserver no ambiente')

    main(parser.parse_args())