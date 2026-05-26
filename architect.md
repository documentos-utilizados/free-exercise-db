# Arquitetura e Organização do Projeto

Este documento descreve a arquitetura, estrutura de arquivos e organização geral do projeto **Free Exercise DB**.

---

## 📁 Estrutura de Diretórios

A estrutura de pastas do projeto é dividida principalmente em duas partes: a **base de dados estruturada (dataset)** e a **aplicação web de busca (frontend)**.

```
free-exercise-db/
├── .github/              # Configurações de CI/CD (GitHub Actions)
├── dist/                 # Arquivos de dados consolidados para distribuição
│   ├── exercises.json    # Base de dados unificada em Inglês
│   └── exercises_pt.json # Base de dados unificada em Português
├── exercises/            # Base original em Inglês (JSONs e imagens)
│   ├── Air_Bike.json     # Metadados de um exercício específico
│   └── Air_Bike/         # Pasta contendo imagens do exercício (.jpg)
├── exercises_pt/         # Base de dados traduzida em Português (apenas JSONs)
├── site/                 # Aplicação web em Vue.js 3 / Vite / Tailwind
│   ├── public/           # Arquivos estáticos do site
│   └── src/              # Código-fonte da aplicação Vue
│       ├── components/   # Componentes interativos da interface
│       ├── App.vue       # Componente principal do Vue
│       └── main.js       # Ponto de entrada do JavaScript
├── translate.py          # Script de tradução offline (Hugging Face)
├── compile_pt.py         # Script de validação e compilação do JSON em PT
├── schema.json           # JSON Schema para validação dos dados dos exercícios
└── Makefile              # Automação de tarefas (linting, build, ndjson)
```

---

## ⚙️ Componentes Arquiteturais

### 1. O Dataset (Banco de Exercícios)
Cada exercício é representado por um documento JSON individual que segue a especificação rigorosa definida no arquivo [schema.json](./schema.json).

Os metadados incluem:
* `id` e `name`: Identificadores e nome do exercício.
* `instructions`: Array com o passo a passo da execução.
* `primaryMuscles` e `secondaryMuscles`: Músculos recrutados.
* `equipment`, `level`, `force`, `mechanic` e `category`: Classificações adicionais do treino.
* `images`: Caminhos relativos para as imagens demonstrativas.

### 2. Pipeline de Tradução e Consolidação
O projeto conta com ferramentas em Python para gerenciamento de dados sem dependência de serviços externos:
* **[translate.py](./translate.py)**: Utiliza inteligência artificial offline (`Helsinki-NLP/opus-mt-tc-big-en-pt`) rodando via PyTorch para traduzir a base original. Possui suporte a fatiamento paralelo (`--num-workers`) para otimização de CPU e dicionários estáticos para garantir precisão nos termos anatômicos.
* **[compile_pt.py](./compile_pt.py)**: Carrega os arquivos traduzidos na pasta `/exercises_pt`, valida-os contra a estrutura padrão e gera o arquivo unificado `/dist/exercises_pt.json`.

### 3. Aplicação Web (Vue.js)
Localizada no diretório `/site`, a interface do usuário permite buscar e favoritar os treinos de maneira reativa.
* **Mecanismo de Busca**: Utiliza a biblioteca `fuse.js` para busca difusa (*fuzzy search*) nos campos de título e instruções.
* **Seletor de Idioma**: O componente `SearchBar.vue` foi arquitetado para chavear dinamicamente as fontes de dados em tempo de execução, permitindo ao usuário alternar a interface entre Português e Inglês instantaneamente sem recarregar a página.
* **Imagens Dinâmicas**: Utiliza a infraestrutura de CDN do `imagekit.io` no componente `PhotoGallery.vue` para servir e redimensionar dinamicamente as fotos a partir do repositório de origem do GitHub.

---

## 🚀 Como Executar Tarefas Comuns

### Validar os JSONs contra o Schema
Para testar a validade estrutural dos JSONs em inglês:
```bash
make lint
```

### Recompilar os JSONs Consolidados
Para gerar o arquivo `/dist/exercises.json` após alterar qualquer arquivo na pasta `/exercises`:
```bash
make dist/exercises.json
```

### Rodar o Site Localmente (Desenvolvimento)
1. Navegue até a pasta `site`:
   ```bash
   cd site
   ```
2. Instale as dependências e inicie o servidor:
   ```bash
   npm install
   npm run dev
   ```
