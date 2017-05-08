#!/usr/bin/env bash

################################################################################
## Configura sistema operaciona
################################################################################

# instalando pacotes necessarios
apt-get update
apt-get install -y postgresql-9.4 unixodbc odbc-postgresql python3 unzip vnc4server fluxbox aterm git


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
## move os arquivos do protheus para dentro da vm
################################################################################

# copia arquivos para outro diretorio
echo "copiando /vagrant para /protheus, aguarde pode demorar..."
cp -R /vagrant /protheus
chown -R vagrant.vagrant /protheus

################################################################################
## instala pacotes do protheus
################################################################################

# instala os arquivos
su - vagrant -c "cd /protheus; python3 protheus.py --install"

################################################################################
## configura o dbaccess para o banco postgres
################################################################################

# verifica library
odbclib=$(du -a /usr/lib/ | grep -i libodbc.so.1 | awk '$1==0{print($2)}')

# configurando o dbaccess para o banco
cat <<EOF > /protheus/bin/dbaccess/dbaccess.ini

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

chown vagrant.vagrant /protheus/bin/dbaccess/dbaccess.ini

################################################################################
## configura o appserver para utilizar esse arquivo
################################################################################

# acessando diretorio do ambiente
cd /protheus

# configurado o appserver
cat <<EOF > ${PWD}/bin/appserver/appserver.ini
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
## preparando interface da vm
################################################################################

mkdir -p /home/vagrant/.vnc

cat <<EOF > /home/vagrant/.vnc/xstartup
#!/bin/sh

[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
vncconfig -iconic &
fluxbox &
EOF

chown -R vagrant.vagrant /home/vagrant
chmod +x /home/vagrant/.vnc/xstartup

################################################################################
## patching vnc4server para nao solicitar senha
################################################################################

(cd / && patch -p1) << \EOF
--- a/usr/bin/vnc4server    2017-04-07 19:28:41.137779800 -0300
+++ b/usr/bin/vnc4server    2017-04-07 19:31:20.064961000 -0300
@@ -41,6 +41,16 @@
 # Global variables.  You may want to configure some of these for your site.
 #
 
+# check disabled password patch
+$password = 1;
+for ($i = 0; $i < scalar @ARGV; $i++) {
+    if ($ARGV[$i] == '-nopasswd') {
+        splice(@ARGV, $i);
+        $password = 0;
+        last;
+    }
+}
+
 $geometry = "1024x768";
 $depth = 16;
 $vncJavaFiles = (((-d "/usr/share/vnc-java") && "/usr/share/vnc-java") ||
@@ -187,7 +197,7 @@
 # Make sure the user has a password.
 
 ($z,$z,$mode) = stat("$vncUserDir/passwd");
-if (!(-e "$vncUserDir/passwd") || ($mode & 077)) {
+if ( (!(-e "$vncUserDir/passwd") || ($mode & 077)) && ($password) ) {
     warn "\nYou will require a password to access your desktops.\n\n";
     system("vncpasswd $vncUserDir/passwd"); 
     if (($? >> 8) != 0) {
@@ -257,7 +267,14 @@
 $cmd .= " -depth $depth" if ($depth);
 $cmd .= " -pixelformat $pixelformat" if ($pixelformat);
 $cmd .= " -rfbwait 30000";
-$cmd .= " -rfbauth $vncUserDir/passwd";
+
+# check password usage
+if ( $password ) {
+    $cmd .= " -rfbauth $vncUserDir/passwd";
+} else {
+    $cmd .= " -SecurityTypes None";
+}
+
 $cmd .= " -rfbport $vncPort";
 $cmd .= " -pn";
EOF

################################################################################
## noVNC
################################################################################

su - vagrant -c "git clone https://github.com/kanaka/noVNC"
echo "http://localhost:6080/vnc.html?host=localhost&port=6080"

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

# inicia o vnc
su - vagrant -c "vncserver :1 -geometry 1024x768 -nopasswd" &

# inciia o noVNC
su - vagrant -c "cd noVNC; sleep 5; ./utils/launch.sh --vnc localhost:5901" &
EOF

chmod +x /etc/rc.local