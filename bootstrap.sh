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
su - vagrant -c "createdb -T template0 -E win1252 -l POSIX protheus"

################################################################################
## configura o data source do odbc
################################################################################

# configurando o odbc no sistema
cat <<EOF > /etc/odbc.ini

; inicio configucacao padrao
[protheus]
Description         = ODBC padrao protheus12
Driver              = PostgreSQL Unicode
Trace               = Yes
TraceFile           = sql.log
Database            = protheus
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

# banco configurado
export TOPDATABASE=POSTGRES

chown vagrant.vagrant /etc/odbc.ini

################################################################################
## instala pacotes do protheus
################################################################################

# instala os arquivos
cd /vagrant
python3 protheus.py --install > variaveis.sh

# ajustes de permissoes
chmod -R 0775 /protheus
chown -R vagrant.vagrant /protheus

# copiando script de controle
cp /vagrant/protheus.py /protheus

# isso vai gerar apartir do install, por enquanto fixo
export RPOLANGUAGE=portuguese
export RPOVERSION=120
export REGIONALLANGUAGE=bra

# carrega informacoes do instalador
source variaveis.sh

# acessando diretorio do ambiente
cd /protheus

################################################################################
## configura o dbaccess para o banco postgres
################################################################################

# verifica library
odbclib=$(du -a /usr/lib/ | grep -i libodbc.so.1 | awk '$1==0{print($2)}')

# configurando o dbaccess para o banco
cat <<EOF > ${PWD}/dbaccess/multi/dbaccess.ini

[General]
LicenseServer=
LicensePort=0
ByYouProc=0

[POSTGRES/protheus]
user=vagrant
password=$(echo -e "\x9e\xff\xe7\xf6\xbf\xb2\x8c")

[POSTGRES]
environments=protheus
clientlibrary=${odbclib}

EOF

# alias configurado
export TOPALIAS=protheus

chown vagrant.vagrant ${PWD}/dbaccess/multi/dbaccess.ini

################################################################################
## configura o appserver para utilizar esse arquivo
################################################################################

# configurado o appserver
envsubst < /vagrant/appserver.ini > ${PWD}/bin/appserver/appserver.ini

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

# start the system
/etc/rc.local