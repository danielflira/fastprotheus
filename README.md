Protheus FastEnv
================

Esse script cria ambientes Protheus para desenvolvimento de forma
rapida atraves da ferramenta vagrant [https://www.vagrantup.com/]

Utilizacao
==========

Uma vez que o vagrant esteja instalado, apenas copiar o repositorio
colocar os arquivos de instalacao na pasta package e executar:

| vagrant up
| vagrant reload

Os pacotes que precisam ser colocados no diretorio package sao:

17-04-18-DBACCESS_LINUX_20161016.TAR.GZ
17-04-20-BRA-DICIONARIOS_COMPL_12_1_16.ZIP
17-04-20-BRA-HELPS_COMPL_12_1_16.ZIP
17-04-20-BRA-MENUS_12_1_16.ZIP
17-04-20-P12_1_16-BRA-EUA-PAR-URU-TTTP120.RPO
17-04-20-P12_BINARIO_LINUX.ZIP
sigaadv.pss
sigapss.spf


bootstrap.sh
- passar diretorios por parametros para o protheus.py

protheus.py
- script protheus.py gerar arquivo de variaveis para carregar