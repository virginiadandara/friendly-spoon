# friendly-spoon

## Descrição
Este projeto tem como objetivo extrair dados sobre um conjunto de candlesticks, organizá-los e tornar fácil o acesso e a extração de informações sobre índices relacionados a eles. Para isso, escolhi o framework do Django ORM para construir o banco de dados e gerenciar suas migrações; no entanto, utilizei apenas a camada de models do framework. O backend do banco escolhido foi o postgresql, devido especialmente a sua boa documentação, a ele ser open source e em especial à sua feature até então exclusiva "select distinct on", que foi útil para selecionar os candlesticks iniciais e finais de cada dia.

Em um primeiro momento, tentei simplesmente extrair os dados para a _média móvel exponencial_ de forma direta, sem fazer um resumo das informaçòes por dia. Embora esse tenha parecido o caminho mais simples, que funcionou inicialmente para a MME, ele se mostrou limitado para encontrar pontos de máximo e mínimo diários, e também para dizer se um dia teve crescimento ou decréscimo ao longo do dia. Por isso, a foi criado um subtipo de candlestick, associado ao dia inteiro, que pega o valor de abertura do primeiro candlestick do dia, o de fechamento do último candlestick do dia, além dos pontos de máximo e mínimo ao longo daquele dia. Esse tipo de candlestick é calculado uma vez após popular o banco, e é salvo usando a mesma tabela com uma coluna "type" que o distingue dos demais. No final, o código foi refatorado para usar o candlestick diário, por sua maior simplicidade e reaproveitabilidade.

Escolhi construir um banco postgres com um uma camada de django embrulhando-o pois, embora fosse possível resolver os problemas dados no processo seletivo através de uso da biblioteca pandas, minha experiência pessoal mostra que raramente um código em pandas é escalável para conjuntos de dados muito grandes, ficando limitado à memória disponível no computador que o executa. Embora, para essa solução, o pandas provavelmente bastasse, na vida real um banco de dados mais robusto seria uma solução mais completa e reaproveitável para construir futuras análises sobre ela - afinal, "nada é tão permanente quanto uma solução temporária".

O código é dividido nas seguintes partes:
* A aplicação candlesticks, que é a única usada para este projeto;
	* `models.py`: o arquivo contendo o model Candlestick responsável pelo armazenamento dos dados da planilha fornecida;
	* `services.py`: o código responsável por calcular índices e por executar queries mais complexas sobre os models;
	* `tests.py`: testes automatizados para garantir que o código não quebre na medida em que ele for modificado e refatorado;
	* `factories.py`: usado para gerar objetos mock para os testes automatizados, a partir da biblioteca `factory_boy`.
	* management/commands: os comandos principais usados para manipular o banco em larga escala.
		* `populate.py`: usado para inserir uma planilha longa de candlesticks no banco
		* `daily_candlesticks.py`: usado para calcular valores de abertura, fechamento, alta e baixa de cada dia, com base nos candlesticks inseridos;
		* `analysis.py`: script que calcula a MME [20, 50, 100, 200] e o IFR [9, 14, 25] de um determinado período, e retorna os dados em formato CSV. Ele chama os serviços definidos em `services.py`.
* A pasta `smarttbot/`, onde as configurações essenciais do projeto estão definidas;
* O arquivo não versionado `key` (localizado na raiz), que contém a chave secreta usada pelo Django para encriptar requisições HTTP e afins. Ele é gerado automaticamente na primeira execução do projeto.

As descrições e a documentação de cada função e cada classe são descritas individualmente em cada arquivo.

## Instalação

### PostgreSQL
É preciso ter o [PostgreSQL instalado](https://www.postgresql.org/download/) e [criar uma database](https://wiki.archlinux.org/index.php/PostgreSQL#Initial_configuration) de nome "smarttbot". A versão mínima requerida do Python é a 3.8.

Também é importante criar um usuário de mesmo nome do usuário atual e com privilégios de superusuário. Um exemplo de script para configuração inicial em distros arch é:

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
python manage.py populate "caminho/para/planilha.csv"
python manage.py daily_candlesticks
```

O segundo comando é responsável por criar um "candlestick-resumo" que diz o valor de abertura, fechamento, máximo e mínimo de cada dia. Os dois procedimentos podem levar alguns minutos, dependendo do tamanho da planilha de entrada.

## Extraindo dados de índices

Para obter uma planilha apropriada, execute o comando abaixo, com as datas em formato ISO:

```bash
python manage.py analysis "data-inicio" "data-final" arquivo-saida.csv
```

Esse comando fornecerá os dados MME20, 50, 100 e 200, além da força bruta relativa 9, 14, e 25.
