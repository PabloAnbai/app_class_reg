# Painel de Avaliação com Machine Learning

Aplicação web Flask para executar modelos de classificação e regressão com arquivos CSV ou XLSX.

## Funcionalidades

- Interface responsiva com tema claro e escuro.
- Seleção de classificação ou regressão.
- Seleção da coluna Target pela interface, com a última coluna como padrão.
- Configuracao da porcentagem de dados reservada para teste.
- Modelos MLP e Random Forest.
- Metricas de classificacao e regressao.
- Assistente de IA em português para recomendar o tipo de problema, modelos e métricas com a API do Google Gemini.
- Testes automatizados que simulam a API do Gemini, sem chamadas de rede.
- Suporte a CSV com codificacao UTF-8, Windows-1252, ISO-8859-1 ou Latin-1.
- Upload limitado a 20 MB.
- Rotas explicitas para impedir o acesso aos arquivos Python internos.

## Tecnologias

- Python 3
- Flask
- Pandas
- NumPy
- scikit-learn
- OpenPyXL
- Tailwind CSS
- JavaScript

## Instalacao

No Linux ou VS Code, dentro da pasta do projeto:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

No Windows, para criar o ambiente virtual:

```powershell
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

## Assistente de IA

Crie um arquivo `.env` a partir do modelo e preencha uma chave da API Gemini:

```bash
cp .env.example .env
```

Abra o `.env` e informe sua chave. O modelo padrão recomendado para projetos
novos é `gemini-3.5-flash-lite`:

```dotenv
GEMINI_API_KEY=sua_chave_api
GEMINI_MODEL=gemini-3.5-flash-lite
```

`GEMINI_MODEL` é opcional; se omitido ou vazio, a aplicação usa
`gemini-3.5-flash-lite`. Os identificadores mudam ao longo do tempo e a
disponibilidade pode variar por conta e região. Confira a [lista oficial de
modelos da API Gemini](https://ai.google.dev/gemini-api/docs/models) e use o
código do modelo (por exemplo, `gemini-3.5-flash-lite`), não o nome exibido
nem um prefixo `models/`. A documentação informa que `gemini-2.5-flash` está
descontinuado e que projetos novos devem usar um modelo mais recente.

O arquivo `.env` já é ignorado pelo Git. Mantenha nele a chave real; nunca a
coloque no `.env.example`, no código-fonte, no navegador ou em commits. Depois
de alterar o `.env`, reinicie o servidor Flask para carregar as variáveis.

Na interface, escreva uma pergunta de até 2.000 caracteres e clique em
**Perguntar**. O arquivo CSV/XLSX é opcional. Se for selecionado, o servidor
envia ao Gemini somente a quantidade de linhas, a quantidade de colunas de
atributos, o tipo da última coluna e a quantidade de valores distintos nela;
o conteúdo completo e os valores das linhas não são enviados.

A rota `POST /api/perguntar` retorna a resposta em português ou um JSON com a
chave `erro`. Erros de chave/permissão, modelo inválido, limite de uso e
problemas de conexão são apresentados como mensagens para orientar a correção.
Se o Gemini retornar erro, confirme que a chave está ativa e que o identificador
do modelo está disponível para ela.

## Executando

Linux ou VS Code:

```bash
venv/bin/python app.py
```

Windows:

```powershell
venv\Scripts\python.exe app.py
```

Para desenvolvimento com recarregamento automático e debugger:

```bash
venv/bin/flask --app app --debug run
```

Acesse:

```text
http://127.0.0.1:5000
```

## Formato dos dados

O arquivo não deve conter cabeçalho de várias linhas. Na interface, selecione a coluna que contém o valor a prever; por padrão, a última coluna é usada.

### Classificação

As colunas usadas como atributos precisam ser numéricas. A coluna Target contém o rótulo da classe.

```csv
area,perimetro,classe
10,20,A
12,22,A
15,28,B
16,30,B
```

Cada classe precisa ter pelo menos duas amostras. O conjunto precisa ter pelo menos quatro linhas validas.

### Regressão

As colunas usadas como atributos e a coluna Target precisam ser numéricas. A coluna Target representa o valor previsto pelo modelo.

```csv
area,perimetro,valor
10,20,35
12,22,38
15,28,44
16,30,47
```

Arquivos XLSX sao lidos com a primeira planilha e a primeira linha pode conter cabecalho.

## Testes

Execute os testes automatizados dentro do ambiente virtual:

```bash
venv/bin/python -m pytest -q
```

No Windows:

```powershell
venv\Scripts\python.exe -m pytest -q
```

Os testes do assistente usam mocks para simular respostas e erros do Gemini; a
suíte não precisa da chave nem acessa a API pela rede.

## Limitacoes

- Os modelos sao treinados novamente a cada requisicao.
- Os uploads nao sao armazenados permanentemente.
- A execucao atual utiliza o servidor de desenvolvimento Flask e nao deve ser exposta diretamente na internet.
- Arquivos maiores que 20 MB sao rejeitados.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).
