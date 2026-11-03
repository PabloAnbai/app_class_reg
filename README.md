# Painel de Avaliação com Machine Learning

Aplicação web Flask para executar modelos de classificação e regressão com arquivos CSV ou XLSX.

## Funcionalidades

- Interface responsiva com tema claro e escuro.
- Seleção de classificação ou regressão.
- Configuracao da porcentagem de dados reservada para teste.
- Modelos MLP e Random Forest.
- Metricas de classificacao e regressao.
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

O arquivo não deve conter cabeçalho de várias linhas.

### Classificação

As colunas anteriores à última precisam ser numéricas. A última coluna contém o rótulo da classe.

```csv
area,perimetro,classe
10,20,A
12,22,A
15,28,B
16,30,B
```

Cada classe precisa ter pelo menos duas amostras. O conjunto precisa ter pelo menos quatro linhas validas.

### Regressão

Todas as colunas precisam ser numéricas. A última coluna representa o valor previsto pelo modelo.

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

## Limitacoes

- Os modelos sao treinados novamente a cada requisicao.
- Os uploads nao sao armazenados permanentemente.
- A execucao atual utiliza o servidor de desenvolvimento Flask e nao deve ser exposta diretamente na internet.
- Arquivos maiores que 20 MB sao rejeitados.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).
