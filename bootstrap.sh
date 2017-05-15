#!/usr/bin/env bash

################################################################################
## Configura sistema operaciona
################################################################################

# instalando pacotes necessarios
apt-get update
apt-get install -y postgresql-9.4 unixodbc odbc-postgresql python3


################################################################################
## Configura o postgres
################################################################################

# criando role para o usuario vagrant
su - postgres -c psql <<EOF
CREATE ROLE vagrant CREATEDB LOGIN PASSWORD 'vagrant';
EOF

# criando banco para o usuario vagrant
su - vagrant -c "createdb -T template0 -E win1252 -l POSIX vagrant"

################################################################################
## configura o data source do odbc
################################################################################

# configurando o odbc no sistema
cat <<EOF > /etc/odbc.ini

; inicio configucacao padrao
[protheus12]
Description         = ODBC padrao protheus12
Driver              = PostgreSQL Unicode
Trace               = Yes
TraceFile           = sql.log
Database            = vagrant
Servername          = localhost
UserName            = vagrant
Password            = vagrant
Port                = 5432
Protocol            = 6.4
ReadOnly            = No
RowVersioning       = No
ShowSystemTables    = No
ShowOidColumn       = No
FakeOidIndex        = No
ConnSettings        =
; termino configucacao padrao

EOF

chown vagrant.vagrant /etc/odbc.ini

################################################################################
## instala pacotes do protheus
################################################################################

# instala os arquivos
cd /vagrant
python3 protheus.py --install

chmod -R 0775 /protheus
chown -R vagrant.vagrant /protheus

cp /vagrant/protheus.py /protheus

################################################################################
## configura o dbaccess para o banco postgres
################################################################################

# verifica library
odbclib=$(du -a /usr/lib/ | grep -i libodbc.so.1 | awk '$1==0{print($2)}')

# configurando o dbaccess para o banco
cat <<EOF > /protheus/dbaccess/multi/dbaccess.ini

[General]
LicenseServer=
LicensePort=0
ByYouProc=0

[POSTGRES/protheus12]
user=vagrant
password=$(echo -e "\x9e\xff\xe7\xf6\xbf\xb2\x8c")

[POSTGRES]
environments=protheus12
clientlibrary=${odbclib}

EOF

chown vagrant.vagrant /protheus/dbaccess/multi/dbaccess.ini

################################################################################
## configura o appserver para utilizar esse arquivo
################################################################################

# acessando diretorio do ambiente
cd /protheus

# configurado o appserver
cat <<EOF > /protheus/bin/appserver/appserver.ini
[PROTHEUS12]
SOURCEPATH=${PWD}/apo
ROOTPATH=${PWD}/protheus_data
STARTPATH=/system/
RPODB=Top
RPOLANGUAGE=portuguese
RPOVERSION=120
TRACE=0
PICTFORMAT=DEFAULT
DATEFORMAT=DEFAULT
LOCALFILES=ctree
LOCALDBEXTENSION=.dtc
REGIONALLANGUAGE=BRA
TOPDATABASE=postgres
TOPSERVER=LOCALHOST
TOPPORT=7890
TOPALIAS=protheus12
HELPSERVER=help.outsourcing.com.br/p12

[Drivers]
ACTIVE=TCP

[TCP]
TYPE=TCPIP
PORT=5555

[LICENSECLIENT]
;SERVER=10.171.65.24
;port=5555

[TDS]
ALLOWAPPLYPATCH=SPOD135
ALLOWEDIT=SPOD1135

[General]
BUILDKILLUSERS=1
SERIE===AV
SEGMENTO=YddTQHWW=VZF=yhu
CONSOLELOG=1

[HTTP]
ENABLE=1
PORT=1080
EOF

chown vagrant.vagrant ${PWD}/bin/appserver/appserver.ini

################################################################################
## inicia o ambiente
################################################################################

# iniciando o dbaccess e appserver
cat << EOF > /etc/rc.local
#!/usr/bin/env bash

cd /protheus

# inicia o protheus
python3 protheus.py --start-dbaccess &
python3 protheus.py --start-appserver &
EOF

chmod +x /etc/rc.local