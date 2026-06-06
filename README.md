# G55 Airline Loyalty — README

## Como arrancar

```bash
cd G55_flask
py -m pip install flask bcrypt matplotlib plotly pandas sqlalchemy
py app.py
```

Abre `http://127.0.0.1:5000` no browser.

Utilizadores de arranque:

| User   | Password | Grupo  |
|--------|----------|--------|
| root   | 1234     | admin  |
| user1  | 12345    | users  |

---

## Estrutura de pastas

```
G55_flask/
├── app.py                  ← ponto de entrada Flask
├── classes/                ← classes de negócio Python
│   ├── gclass.py           ← classe base genérica (CRUD + navegação)
│   ├── airline.py
│   ├── promotion.py
│   ├── reward.py
│   ├── redemption.py
│   └── userlogin.py        ← gestão de utilizadores com bcrypt
├── data/
│   └── G55.db              ← base de dados SQLite
├── static/css/
│   └── main.css
├── subs/                   ← lógica de cada rota (backend)
│   ├── apps_gform.py       ← CRUD genérico para todas as classes
│   ├── apps_userlogin.py   ← CRUD de utilizadores
│   ├── apps_plot.py        ← gráficos Matplotlib (PNG estático)
│   └── apps_plotly.py      ← dashboard interactivo Plotly (6 gráficos)
└── templates/              ← páginas HTML (Jinja2)
    ├── base.html           ← template base com nav
    ├── home.html
    ├── login.html
    ├── gform.html          ← formulário CRUD genérico + tabela completa
    ├── userlogin.html
    ├── plot.html
    └── plotly.html
```

---

## Flask — como funciona

### O que é Flask

Flask é uma framework Python minimalista para criar aplicações web.
O conceito central é o **decorator de rota**: associa um URL a uma função Python.

```python
@app.route("/gform/<cname>", methods=["post", "get"])
def gform(cname):
    return apps_gform(cname)
```

Quando o browser acede a `/gform/Airline`, Flask chama `gform("Airline")`.
`methods=["post","get"]` indica que a rota aceita tanto pedidos GET (navegação/botões)
como POST (submissão de formulários).

### app.py

É o ponto de entrada. Faz três coisas ao arrancar:

1. **Carrega os dados** uma única vez para memória com `Airline.load_db(DB_PATH)`
   e `Userlogin.read(DB_PATH)`.
2. **Define as rotas** — cada URL mapeia para uma função nos `subs/`.
3. **Protege as rotas** com `require_login()`: se não houver sessão activa,
   redireciona para `/login`.

### Rotas disponíveis

| URL | Método | Descrição |
|-----|--------|-----------|
| `/` | GET | Página inicial com contagens |
| `/login` | GET | Formulário de login |
| `/logoff` | GET | Termina a sessão |
| `/chklogin` | POST | Valida credenciais |
| `/gform/<cname>` | GET/POST | CRUD de Airline, Promotion, Reward, Redemption |
| `/Userlogin` | GET/POST | Gestão de utilizadores |
| `/plot` | GET | Gráficos Matplotlib |
| `/plotly` | GET | Dashboard interactivo Plotly |

### Sessões Flask

Flask usa **sessões do lado do servidor** baseadas em cookies assinados.
`session["user"] = user` guarda o nome do utilizador autenticado.
`session.pop("user", None)` apaga-o no logoff.
`session.get("user")` retorna `None` se não estiver autenticado.

A `secret_key` é usada para assinar o cookie — em produção deve ser uma string
longa e aleatória.

### Templates Jinja2

Os templates HTML usam Jinja2 (motor de templates do Flask):

```html
{{ variavel }}           ← imprime o valor de uma variável
{% if condição %}        ← condicional
{% for item in lista %}  ← ciclo
{% extends "base.html" %} ← herança de templates
{% block content %}      ← zona substituível pelo template filho
{{ variavel | safe }}    ← imprime HTML sem escapar (usado para o Plotly)
```

O `render_template("gform.html", cname=cname, att=cls.att, ...)` passa
variáveis do Python para o template.

### apps_gform.py — CRUD genérico

Em vez de criar um ficheiro separado por classe, `apps_gform` serve todas
as classes dinamicamente:

1. Recebe `cname` (ex: `"Promotion"`) e resolve a classe via um dicionário registry.
2. Lê `cls.att` para saber os campos: `['promotion_id','name','min_miles',...]`.
3. Constrói o formulário e a tabela automaticamente — o template `gform.html`
   itera `att` com um `{% for field in att %}`.
4. Para campos FK (`reward_id`, `promotion_id`) mostra um dropdown com
   os registos da classe referenciada.
5. No save, valida datas antes de chamar `cls.from_string()` e `cls.insert()`.

A variável `prev_option` é guardada por classe num dicionário `_prev_options`
para distinguir se o Save vem de um Insert ou de um Edit.

---

## Pandas e gráficos

### Como os dados são lidos

```python
from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/G55.db')
df_red = pd.read_sql('SELECT * FROM Redemption', engine)
```

`pd.read_sql` lê a tabela directamente para um DataFrame pandas — uma tabela
em memória com colunas tipadas. É a ponte entre o SQLite e o pandas.

### Operações pandas usadas

```python
# Agrupar e somar — total de milhas por airline
merged.groupby('name')['miles_used'].sum()

# Ordenar e seleccionar top 10
.sort_values(ascending=True).tail(10)

# Juntar tabelas (equivalente a SQL JOIN)
df_red.merge(df_ap, on='promotion_id')
      .merge(df_air[['airline_id','name']], on='airline_id')

# Converter datas e extrair dia da semana
df_red['redemption_date'] = pd.to_datetime(df_red['redemption_date'])
df_red['dow'] = df_red['redemption_date'].dt.dayofweek

# Tabela pivot para o heatmap
heatmap_df.pivot(index='dow', columns='weekno', values='count').fillna(0)
```

### apps_plot.py — Matplotlib

Matplotlib gera imagens PNG estáticas. O processo é:

1. Criar figura com `plt.subplots(2, 2, figsize=(14, 10))`
2. Desenhar cada gráfico num eixo (`ax`)
3. Guardar em memória: `plt.savefig(buf, format='png')`
4. Codificar em base64 para embutir directamente no HTML:
   `base64.b64encode(buf.getvalue()).decode('utf-8')`
5. Passar ao template: `<img src="data:image/png;base64,{{ image }}">`

### apps_plotly.py e apps_plotly2.py — Plotly

Plotly gera HTML+JavaScript interactivo. O processo é:

1. Criar figura com `make_subplots(rows=..., cols=...)`
2. Adicionar traces: `fig.add_trace(go.Bar(...), row=1, col=1)`
3. Converter para HTML: `fig.to_html(full_html=False, div_id='my-plot')`
4. Passar ao template: `{{ plot_div | safe }}` (o `| safe` evita que o Jinja2
   escape o HTML gerado pelo Plotly)

Tipos de gráficos usados:

| Ficheiro | Gráfico | Tipo Plotly |
|----------|---------|-------------|
| plotly.py | Airlines por milhas | `go.Bar` horizontal |
| plotly.py | Redemptions semanais | `go.Scatter` com área |
| plotly.py | Distribuição de milhas | `go.Histogram` |
| plotly.py | Top passageiros | `go.Bar` horizontal |
| plotly.py | Milhas por reward | `go.Pie` (donut) |
| plotly.py | Intensidade por dia/semana | `go.Heatmap` |

---

## Userlogin — como funciona

### A classe Userlogin

`Userlogin` herda de `Gclass` e representa um utilizador da aplicação.
Tem 4 atributos: `_id`, `_user`, `_usergroup`, `_password`.

Os atributos `_user`, `_usergroup` e `_password` têm **underscores** porque
os campos na BD SQLite também se chamam `_user`, `_usergroup`, `_password`.
O `_password` nunca é devolvido directamente (a property `password` retorna
sempre `""`), para impedir que a password encriptada seja exposta.

### Encriptação de passwords com bcrypt

bcrypt é um algoritmo de hashing especificamente desenhado para passwords.
Ao contrário de MD5 ou SHA, é deliberadamente lento e inclui um **salt**
aleatório em cada hash, o que torna ataques de força bruta muito mais difíceis.

```python
# Encriptar (ao criar/alterar password)
passencrypted = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Resultado ex: b'$2b$12$abcdef...xyz' — inclui o salt embutido

# Verificar (ao fazer login)
valid = bcrypt.checkpw(password.encode(), obj._password.encode())
# Não é necessário guardar o salt separadamente — está embutido no hash
```

### Fluxo de autenticação

```
Browser                    Flask (app.py)             Userlogin
   |                            |                          |
   |-- POST /chklogin -------> |                          |
   |   {user, password}        |-- chk_password(u,p) --> |
   |                            |                    valida bcrypt
   |                            |   "Valid" <-------------|
   |                            |                          |
   |                    session["user"] = user             |
   |                    Userlogin.username = user          |
   |                    Userlogin.user_id  = id            |
   |<-- redirect / ------------|                          |
```

Se a validação falhar, `chk_password` retorna `"Wrong password"` ou
`"No existent user"`, e a página de login volta a ser mostrada com
a mensagem de erro.

### Variáveis de classe

Após login bem sucedido, dois valores ficam guardados como variáveis de classe:

- `Userlogin.username` — nome do utilizador autenticado (ex: `"root"`)
- `Userlogin.user_id`  — id do utilizador autenticado (ex: `1`)

Estas variáveis permitem saber em qualquer momento se há alguém autenticado
e quem é, sem precisar de consultar a BD.

### Grupos e permissões

Existem dois grupos:

| Grupo | Permissões |
|-------|-----------|
| `admin` | Ver todos os utilizadores, criar, editar (user + grupo + password), apagar, navegar |
| `users` | Ver apenas o próprio registo, editar só a password |

A lógica de permissões está em `apps_userlogin.py` e no template `userlogin.html`.
O grupo do utilizador actual é determinado em cada pedido:

```python
uid = Userlogin.get_user_id(session.get("user"))
group = Userlogin.obj[uid]._usergroup  # "admin" ou "users"
```

O template usa `{% if group == "admin" %}` para mostrar ou esconder
os botões Delete, Insert, e a tabela completa de utilizadores.

### Tabela Userlogin na BD

```sql
CREATE TABLE Userlogin (
    _id        INTEGER PRIMARY KEY,
    _user      TEXT    NOT NULL UNIQUE,
    _usergroup TEXT    NOT NULL,
    _password  TEXT    NOT NULL    -- hash bcrypt, nunca a password em claro
);
```

A password nunca é guardada em claro na BD — apenas o hash bcrypt,
que não pode ser revertido para obter a password original.
