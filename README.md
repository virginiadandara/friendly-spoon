# friendly-spoon

## Instalação

### PostgreSQL
É preciso ter o PostgreSQL instalado e criar uma database de nome "smarttbot". A versão mínima requerida do Python é a 3.8.

https://www.postgresql.org/download/
https://wiki.archlinux.org/index.php/PostgreSQL#Initial_configuration

Também é importante criar um usuário de mesmo nome do usuário atual e com privilégios de superusuário. Um exemplo de script em distros arch é:
```bash
initdb -D /var/lib/postgres/data
systemctl start postgresql
systemctl enable postgresql
createuser --interactive
```

Depois, crie a database com nome apropriado:
```bash
createdb smarttbot
```

### Ambiente Python
Uma vez que o python 3.8 esteja instalado, mude para a pasta raiz desse diretório e crie um ambiente virtual com o comando
```bash
python3.8 -m venv venv
source venv/bin/activate
```

Uma vez ativado o ambiente virtual, instale os pacotes necessários:
```bash
pip install -r requirements
```

Depois, faça as migrações:
```bash
python manage.py migrate
```

Se tudo estiver correto, o comando abaixo deve ser executado com sucesso:
```bash
python manage.py test
```

## Alimentando o banco
Para inserir dados no banco a partir de uma planilha de candlesticks, use o comando
```bash
python manage.py populate [caminho/para/planilha.csv]
python manage.py daily_candlesticks
```

O segundo comando é responsável por criar um "candlestick-resumo" que diz o valor de abertura, fechamento, máximo e mínimo de cada dia. Os dois procedimentos podem levar alguns minutos, dependendo do tamanho da planilha de entrada.



