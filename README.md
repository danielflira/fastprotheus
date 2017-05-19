fastprotheus
============
Repositório Vagrant para criação de ambiente com Protheus em ambiente Linux


**o que vai precisar:**
- Pacotes Protheus
  - dbaccess
  - binario
  - menus
  - dicionarios
  - repositorio
  - helps
  - sigaadv.pss
  - sigapss.sfp


**o que repositório possui:**
- Vagrantfile
- bootstrap.sh
- protheus.py
- appserver.ini


Como utilizar
=============

É necessário apenas ter as ferramentas instaladas (Virtual e Vagrant).
Fazer uma cópia deste repositório. Obter os arquivos acima listados e 
coloca-los no subdiretório "packages". Então executar os seguintes 
comandos:


```
$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'bento/debian-8.2-i386'...
==> default: Matching MAC address for NAT networking...
...
==> default: 2017-05-19 22:20:23,934 INFO: arquivo (sigapss.spf)



$ vagrant reload
==> default: Attempting graceful shutdown of VM...
...

```


Detalhe do que precisa
======================


**Pacotes Protheus**

Pegar os pacotes de instalação do Protheus no portal, normalmente contendo
os nomes baseados nas seguintes regras:

- [YY-MM-DD]-[VERSAO]_BINARIO_LINUX.ZIP
- [YY-MM-DD]-DBACCESS_LINUX_[RELEASE].TAR.GZ
- [YY-MM-DD]-BRA-DICIONARIOS_COMPL_[VERSAO].ZIP
- [YY-MM-DD]-BRA-MENUS_[VERSAO].ZIP
- [YY-MM-DD]-[VERSAO]-BRA-EUA-PAR-URU-[TTTP110|TTTP120].RPO
- [YY-MM-DD]-BRA-HELPS_COMPL_[VERSAO].ZIP

Os seguintes arquivos presentes na system de algum ambiente também devem 
ser colocados no diretório packages:

- sigaadv.pss
- sigapss.spf


Detalhe do repositório
======================


**Vagrantfile**

Arquivo de configuração do Vagrant com Debian 8.2


**bootstrap.sh**

Responsável por instalar banco de dados, instalar e configurar unixodbc, 
extrair arquivos dos pacotes do Protheus e instalar, configurar DbAccess, 
configurar o AppServer e preparar a inicialização da vm.


**protheus.py**

Responsável por extrair pacotes do Protheus, controlar execução do DbAccess
e a execução do AppServer.


**appserver.ini**

Apenas um arquivo com o modelo de configuração do AppServer. O arquivo 
possui alguns marcadores para que possa ser substituido com informações 
da vm e instalação. Exemplo: a entrada _TOPDATABASE_ é configurada baseada
no banco de dados que foi instalado na vm.


O que será feito
================

- bootstrap.sh com outros bancos de dados
- protheus.py receber diretórios por parâmetro
- protheus.py gerar informações das variaveis do appserver.ini