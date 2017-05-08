#!/usr/bin/python

import subprocess, os, shutil, stat, argparse


def unzip_to(filename, changedir='.'):
    subprocess.check_output(['unzip', filename, '-d', changedir])


def untar_to(filename, changedir='.'):
    subprocess.check_output(['tar', '-xzf', filename, '-C', changedir])


def clean_sandbox():
    shutil.rmtree('sandbox')
    create_sandbox()


def create_sandbox():
    try:
        os.mkdir('sandbox')
    except:
        pass


def try_remove(filepath):
    try:
        os.remove(filepath)
    except PermissionError:
        os.chmod(filepath, stat.S_IWUSR)
        os.remove(filepath)


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


def move_to(location1, location2):
    for root, dirs, files in os.walk(location1):
        for filename in files:
            filepath1 = os.path.join(root, filename)
            # adjust dest path
            filepath2 = filepath1.split(os.sep)
            filepath2[0] = location2
            filepath2 = os.path.join(*filepath2)
            try:
                shutil.copy2(filepath1, filepath2)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(filepath2))
                shutil.copy2(filepath1, filepath2)
            except PermissionError:
                os.chmod(filepath2, stat.S_IWUSR)
                shutil.copy2(filepath1, filepath2)


def _install_binary(package, params):
    print('instalando pacote binario {0}'.format(package))
    clean_sandbox()
    unzip_to(package, 'sandbox')

    # descompacta tudo!
    unpack = True
    while unpack:
        unpack = False
        for root, dirs, files in os.walk('sandbox'):
            for filename in files:
                filepath = os.path.join(root, filename)
                extension = os.path.splitext(filepath)[1]

                if extension.lower() in ['.gz', '.z']:
                    print('untar {0} to {1}'.format(filepath, root))
                    untar_to(filepath, root)
                    try_remove(filepath)
                    unpack = True

                if extension.lower() in ['.zip']:
                    print('unzip {0} to {1}'.format(filepath, root))
                    unzip_to(filepath, root)
                    try_remove(filepath)
                    unpack = True

            if 'appsrvlinux' in files:
                print('renomeando {0} para {1}'.format('appsrvlinux',
                        'appserver'))
                os.rename(os.path.join(root, 'appsrvlinux'),
                        os.path.join(root, 'appserver'))

    # busca o ace de versao maior
    maior_ace = ''
    for root, dirs, files in os.walk('sandbox'):
        for dirname in dirs:
            if dirname.lower().startswith('ace'):
                if dirname > maior_ace:
                    maior_ace = dirname

    # copia dados do maior ace no appserver
    for root, dirs, files in os.walk('sandbox'):
        if root.lower().endswith(maior_ace):
            upperdir = os.path.join(root, '..')
            for filename in files:
                filepath = os.path.join(root, filename)
                print('copiando {0} para {1}'.format(filepath, upperdir))
                shutil.copy2(filepath, upperdir)

    # ultimos ajustes
    for root, dirs, files in os.walk('sandbox'):
        if 'appserverLinux' in dirs:
            print('renomeando {0} para {1}'.format('appserverLinux',
                    'appserver'))
            os.rename(os.path.join(root, 'appserverLinux'),
                    os.path.join(root, 'appserver'))

        if 'smartclientLinux' in dirs:
            print('renomeando {0} para {1}'.format('smartclientLinux',
                    'smartclient'))
            os.rename(os.path.join(root, 'smartclientLinux'),
                    os.path.join(root, 'smartclient'))

    # ajustando as configuracao do sandbox
    print('movendo {0} para {1}'.format('sandbox', 'bin'))
    move_to('sandbox', 'bin')


def _install_dbaccess(package, params):
    print('instalando pacote dbaccess {0}'.format(package))
    clean_sandbox()

    dbaccess = os.path.join('sandbox', 'dbaccess')
    os.makedirs(dbaccess)
    untar_to(package, dbaccess)

    # copia dados do maior ace no appserver
    for root, dirs, files in os.walk('sandbox'):
        if root.lower().endswith('multi'):
            upperdir = os.path.join(root, '..')
            for filename in files:
                filepath = os.path.join(root, filename)
                print('copiando {0} para {1}'.format(filepath, upperdir))
                shutil.copy2(filepath, upperdir)
            shutil.rmtree(root)

        # corrigindo permissao do dbmonitor
        if 'dbmonitor' in files:
            filepath = os.path.join(root, 'dbmonitor')
            os.chmod(filepath,  stat.S_IRWXU|stat.S_IRGRP|
                    stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

    print('movendo {0} para {1}'.format('sandbox', 'bin'))
    move_to('sandbox', 'bin')


def _install_dictionary(package, params):
    print('instalando pacote dicionario {0}'.format(package))
    clean_sandbox()

    systemload = os.path.join('sandbox', 'systemload')
    unzip_to(package, systemload)

    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.startswith('hlp'):
                move_to(root, '..')

    print('movendo {0} para {1}'.format('sandbox', 'protheus_data'))
    move_to('sandbox', 'protheus_data')

def _install_helps(package, params):
    print('instalando pacote helps {0}'.format(package))
    clean_sandbox()

    systemload = os.path.join('sandbox', 'systemload')
    unzip_to(package, systemload)

    print('movendo {0} para {1}'.format('sandbox', 'protheus_data'))
    move_to('sandbox', 'protheus_data')


def _install_menus(package, params):
    print('instalando pacote menus {0}'.format(package))
    clean_sandbox()

    system = os.path.join('sandbox', 'system')
    unzip_to(package, system)

    os.mkdir(os.path.join(system, 'data'))

    print('movendo {0} para {1}'.format('sandbox', 'protheus_data'))
    move_to('sandbox', 'protheus_data')


def _install_rpo(package, params):
    print('instalando pacote apo {0}'.format(package))
    clean_sandbox()

    rpo = package.split('-')[-1].lower()
    rpo = os.path.join('sandbox', rpo)
    shutil.copy2(package, rpo)

    print('movendo {0} para {1}'.format('sandbox', 'apo'))
    move_to('sandbox', 'apo')


def _install_pss(package, params):
    print('instalando pacote pss {0}'.format(package))
    clean_sandbox()

    system = os.path.join('sandbox', 'system', package)
    os.makedirs(os.path.dirname(system))
    shutil.copy2(package, system)

    print('movendo {0} para {1}'.format('sandbox', 'protheus_data'))
    move_to('sandbox', 'protheus_data')


# fixme: adicionado como contorno pois appserver nao esta gerando automaticamente
def _install_spf(package, params):
    print('instalando pacote spf {0}'.format(package))
    clean_sandbox()

    system = os.path.join('sandbox', 'system', package)
    os.makedirs(os.path.dirname(system))
    shutil.copy2(package, system)

    print('movendo {0} para {1}'.format('sandbox', 'protheus_data'))
    move_to('sandbox', 'protheus_data')


def _install_appserverini(package, params):
    print('instalando pacote {0}'.format(package))
    clean_sandbox()

    system = os.path.join('sandbox', 'appserver', 'appserver.ini')
    os.makedirs(os.path.dirname(system))
    shutil.copy2(package, system)

    print('movendo {0} para {1}'.format('sandbox', 'bin'))
    move_to('sandbox', 'bin')


def install_packages(params):
    create_sandbox()

    for i in os.listdir('.'):
        backup = False

        if 'bina' in i.lower():
            _install_binary(i, params)
            backup = True

        if 'menu' in i.lower():
            _install_menus(i, params)
            backup = True

        if 'dbac' in i.lower():
            _install_dbaccess(i, params)
            backup = True

        if 'dici' in i.lower() and 'compl' in i.lower():
            _install_dictionary(i, params)
            backup = True

        if 'help' in i.lower() and 'compl' in i.lower():
            _install_helps(i, params)
            backup = True

        if i.lower().endswith('.rpo'):
            _install_rpo(i, params)
            backup = True

        if i.lower().endswith('.pss'):
            _install_pss(i, params)
            backup = True

        # fixme: adicionado como contorno pois appserver nao esta gerando
        if i.lower().endswith('.spf'):
            _install_spf(i, params)
            backup = True

        if i.lower().endswith('appserver.ini'):
            _install_appserverini(i, params)
            backup = True

        if backup:
            try:
                os.mkdir('backup')
                shutil.move(i, 'backup')
            except:
                shutil.move(i, 'backup')

    shutil.rmtree('sandbox')


def main(args):
    if args.install:
        install_packages(args)
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
