# 🅿️ API de Gerenciamento de Estacionamento

Uma API REST completa desenvolvida com Flask para gerenciar estacionamentos, incluindo autenticação de usuários, controle de vagas, registro de veículos e histórico de entradas/saídas.

## ⚠️ Antes de Começar

**Importante:** Este projeto inclui um backup completo do banco de dados em `db/parking_service_backup.sql`. 

Para começar rapidamente:

```bash
# 1. Restaure o banco de dados
mysql -u root -p < db/parking_service_backup.sql

# 2. Configure variáveis de ambiente
cp .env-example .env
# Edite .env com suas credenciais

# 3. Instale dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

**Login de Teste:** testejose / testejose

---

## 📋 Sumário
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints](#endpoints)
- [Autenticação](#autenticação)
- [Documentação Adicional](#documentação-adicional)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## ✨ Características

✅ **Autenticação Completa**
- Registro de novo usuários
- Login com sessões seguras
- Logout
- Recuperação de senha via email

✅ **Gerenciamento de Vagas**
- CRUD de vagas de estacionamento
- Rastreamento de disponibilidade
- Associação com tipos de veículos

✅ **Registro de Veículos**
- CRUD de veículos
- Classificação por tipo
- Informações do proprietário

✅ **Histórico de Entradas/Saídas**
- Registro de horário de entrada
- Registro de horário de saída
- Histórico completo de movimentação

✅ **Segurança**
- Proteção de rotas com autenticação obrigatória
- Credenciais em variáveis de ambiente
- Gerenciamento de sessões Flask
- Validação de entrada
---

## 📦 Requisitos

- **Python** 3.8+
- **MySQL** 5.7+
- **pip** (gerenciador de pacotes Python)

### Dependências do Projeto

```
Flask==3.1.3
PyMySQL==1.1.3
python-dotenv==1.2.2
Flask-Mail==0.9.1
Werkzeug==3.0.0
Blinker==1.7.0
```

---

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/joseantonioalmeida/API-FLASK-ESTACIONAMENTO.git
cd API-FLASK-ESTACIONAMENTO
```

### 2. Crie um Ambiente Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados

#### Opção A: Restaurar do Backup (Recomendado)

Se você possui o arquivo de backup do banco:

```bash
# Importe o backup completo (cria a database automaticamente)
mysql -u root -p < db/parking_service_backup.sql
```

**Resultado:**
- ✅ Banco de dados `parking_service` criado automaticamente
- ✅ Todas as tabelas criadas com estrutura correta
- ✅ Dados de exemplo importados
- ✅ Relacionamentos e constraints configurados


**Tabelas Criadas Automaticamente (com backup):**
- `auth_user` - Autenticação e usuários
- `customer` - Clientes e proprietários
- `vehicle` - Veículos registrados
- `vehicle_type` - Tipos de veículos (carro, moto, etc)
- `parking_spot` - Vagas de estacionamento
- `parking_record` - Histórico de entradas/saídas

### 5. Configure as Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env-example .env

# Edite o arquivo .env com suas credenciais
nano .env  # ou use seu editor de texto favorito
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database Configuration
db_host=localhost
db_user=seu_usuario_mysql
db_password=sua_senha_mysql
db_name=parking_service

# Flask Configuration
secret_key=sua_chave_secreta_super_segura

# Email Configuration (Gmail SMTP)
mail_server=smtp.gmail.com
mail_port=587
mail_use_tls=True
mail_username=seu_email@gmail.com
mail_password=sua_senha_app_gmail
```

### Configuração do Gmail SMTP

1. **Ative 2FA no Gmail**: https://myaccount.google.com/security
2. **Gere uma Senha de Aplicativo**: https://myaccount.google.com/apppasswords
3. **Configure em .env**: Use a senha gerada no campo `mail_password`

### Arquivo .env-example

Um arquivo `.env-example` é fornecido como template. Desenvolvedores novos devem:

```bash
cp .env-example .env
# Depois preencher com suas credenciais reais
```

---

## 🎯 Como Usar

### 0. Restaure o Banco de Dados (Importante!)

Antes de iniciar o servidor, importe o backup do banco:

```bash
# Importe o backup completo
mysql -u root -p < db/parking_service_backup.sql

# Verifique se foi importado
mysql -u root -p -e "USE parking_service; SHOW TABLES;"
```

**Ou veja a seção [Estrutura do Banco de Dados](#-estrutura-do-banco-de-dados) para detalhes.**

---

### 1. Inicie o Servidor
```bash
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

### 2. Exemplos de Requisições

#### 🔐 Use Credenciais de Teste

Após importar o backup, você tem um usuário para testar:

```json
{
  "username": "testejose",
  "password": "testejose"
}
```

---

#### Registrar Novo Usuário
```bash
curl -X POST http://localhost:5000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario123",
    "email": "usuario@gmail.com",
    "password": "senha123"
  }'
```

#### Fazer Login
```bash
curl -X POST http://localhost:5000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario123",
    "password": "senha123"
  }'
```

#### Listar Vagas (Requer Autenticação)
```bash
curl -X GET http://localhost:5000/parking-spots/ \
  -H "Cookie: session=seu_session_id"
```

#### Criar Vaga
```bash
curl -X POST http://localhost:5000/parking-spots/ \
  -H "Content-Type: application/json" \
  -H "Cookie: session=seu_session_id" \
  -d '{
    "numero": "A-01",
    "tipo_veiculo_id": 1,
    "disponivel": true
  }'
```

### 3. Testar com Postman

1. Configure as variáveis de ambiente
2. Execute as requisições em sequência

---

## 📂 Estrutura do Projeto

```
API-FLASK-ESTACIONAMENTO/
│
├── app.py                              # Aplicação principal Flask
├── requirements.txt                    # Dependências do projeto
├── .env                                # Variáveis de ambiente (NÃO commitar)
├── .env-example                        # Template de variáveis de ambiente
├── .gitignore                          # Arquivos ignorados pelo Git
│
├── db/
│   └── connect_db.py                  # Conexão com banco de dados
│   └── parking_service_backup.sql     # 📦 Backup completo do banco (importar com MySQL)
│
├── views/
│   ├── auth_view.py                   # 🔐 Rotas de autenticação
│   ├── auth_user_view.py              # Usuários (adicional)
│   ├── customers_view.py              # 👥 Gerenciamento de clientes
│   ├── parking_record_view.py         # 📝 Histórico de entradas/saídas
│   ├── parking_spot_view.py           # 🅿️ Gerenciamento de vagas
│   ├── vehicle_type_view.py           # 🚗 Tipos de veículos
│   └── vehicle_view.py                # 🚘 Gerenciamento de veículos
│
├── utils.py                            # 🔒 Decorator @login_required
│
├─  README.md                       # Este arquivo
```

---

## �️ Estrutura do Banco de Dados

### Backup Disponível

O arquivo de backup completo está em:
```
db/parking_service_backup.sql
```

Este arquivo contém:
- ✅ Estrutura de todas as 6 tabelas
- ✅ Dados de exemplo para testes
- ✅ Relacionamentos e constraints
- ✅ Índices otimizados

### Tabelas Principais

#### 1. `auth_user` - Autenticação
Armazena credenciais e informações dos usuários do sistema.

```sql
Campos:
- id (bigint, PK) - ID único
- username (varchar) - Único, para login
- password (varchar) - Senha do usuário
- email (varchar) - Email único
- first_name (varchar) - Primeiro nome
- last_name (varchar) - Sobrenome
- is_superuser (tinyint) - É administrador?
- is_staff (tinyint) - É staff?
- is_active (tinyint) - Usuário ativo?
- date_joined (datetime) - Data de criação
- last_login (datetime) - Último acesso
```

**Dados de Exemplo:**
- `testejose` / `testejose` - Superuser

---

#### 2. `customer` - Clientes/Proprietários
Informações dos clientes que usam o estacionamento.

```sql
Campos:
- id (bigint, PK) - ID único
- user_id (bigint, FK) - Referência ao usuário (opcional)
- name (varchar) - Nome completo
- cpf (varchar) - CPF do cliente
- phone (varchar) - Telefone de contato
- created_at (datetime) - Data de criação
- updated_at (datetime) - Última atualização
```

**Relacionamentos:**
- Pode ter múltiplos veículos (1:N com vehicle)
- Pode estar associado a um usuário (1:1 com auth_user)

---

#### 3. `vehicle_type` - Tipos de Veículos
Categorias de veículos suportados pelo estacionamento.

```sql
Campos:
- id (bigint, PK) - ID único
- name (varchar) - Nome do tipo (Ex: Carro, Moto, Bicicleta)
- description (text) - Descrição/observações
```

**Exemplos de Dados:**
- `Carro` - Automóvel de 4 rodas
- `Moto` - Motocicleta
- `Bicicleta` - Bicicleta

---

#### 4. `vehicle` - Veículos
Todos os veículos registrados no sistema.

```sql
Campos:
- id (bigint, PK) - ID único
- vehicle_type_id (bigint, FK) - Tipo do veículo
- license_plate (varchar) - Placa única
- brand (varchar) - Marca (Ex: Chevrolet, Honda)
- model (varchar) - Modelo (Ex: Opala, Civic)
- color (varchar) - Cor do veículo
- owner_id (bigint, FK) - Proprietário (customer)
- created_at (datetime) - Data de cadastro
- updated_at (datetime) - Última atualização
```

**Relacionamentos:**
- Pertence a um tipo (N:1 com vehicle_type)
- Pertence a um cliente (N:1 com customer)
- Pode ter múltiplos registros (1:N com parking_record)

**Dados de Exemplo:**
- `DEF5678` - Chevrolet Opala Preto
- `ABC4321` - Chevrolet Marea Prata

---

#### 5. `parking_spot` - Vagas de Estacionamento
Vagas físicas disponíveis no estacionamento.

```sql
Campos:
- id (bigint, PK) - ID único
- spot_number (varchar) - Número da vaga (Ex: 001, 002)
- is_occupied (tinyint) - Vaga ocupada?
- created_at (datetime) - Data de criação
- updated_at (datetime) - Última atualização
```

**Dados de Exemplo:**
- `001` - Vaga ocupada/desocupada
- `002` - Vaga ocupada/desocupada

---

#### 6. `parking_record` - Histórico de Movimentação
Registro de todas as entradas e saídas de veículos.

```sql
Campos:
- id (bigint, PK) - ID único
- vehicle_id (bigint, FK) - Veículo que entrou
- parking_spot_id (bigint, FK) - Vaga utilizada
- entry_time (datetime) - Hora de entrada
- exit_time (datetime) - Hora de saída (NULL se ainda dentro)
- created_at (datetime) - Data do registro
- updated_at (datetime) - Última atualização
```

**Relacionamentos:**
- Referencia um veículo (N:1 com vehicle)
- Referencia uma vaga (N:1 com parking_spot)

**Status Dinâmico:**
- `exit_time IS NULL` = Veículo ainda dentro
- `exit_time IS NOT NULL` = Veículo já saiu

---

### Diagrama de Relacionamentos

```
┌─────────────────┐
│   auth_user     │
│ (Autenticação)  │
└────────┬────────┘
         │ 1:1 (opcional)
         │
         ▼
┌─────────────────┐
│    customer     │
│ (Proprietários) │
└────────┬────────┘
         │ 1:N
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│    vehicle      │◄─────┤  vehicle_type   │
│  (Veículos)     │ N:1  │  (Categorias)   │
└────────┬────────┘      └─────────────────┘
         │ 1:N
         ▼
┌─────────────────┐
│ parking_record  │
│ (Entradas/Saí)  │
└────────┬────────┘
         │ N:1
         ▼
┌─────────────────┐
│  parking_spot   │
│    (Vagas)      │
└─────────────────┘
```

---

### Como Restaurar o Backup

#### Passo 1: Verifique o Arquivo
```bash
# Verifique se o arquivo existe
ls db/parking_service_backup.sql
# ou
dir db\parking_service_backup.sql  # Windows
```

#### Passo 2: Importe para MySQL
```bash
# Windows
mysql -u root -p < db/parking_service_backup.sql

# Linux/macOS
mysql -u root -p < db/parking_service_backup.sql
```

#### Passo 3: Confirme a Importação
```bash
# Acesse MySQL
mysql -u root -p

# Na linha de comando do MySQL
USE parking_service;
SHOW TABLES;

# Deve listar:
# +------------------------+
# | Tables_in_parking_service |
# +------------------------+
# | auth_user              |
# | customer               |
# | parking_record         |
# | parking_spot           |
# | vehicle                |
# | vehicle_type           |
# +------------------------+

# Ver dados de exemplo
SELECT * FROM auth_user;
SELECT * FROM vehicle;
SELECT * FROM parking_spot;
EXIT;
```

---

### Dados de Teste Disponíveis

Após restaurar o backup, você tem:

**Usuários para Login:**
```
Username: testejose
Password: testejose
```

**Clientes (20 registros):**
- Teste 2 put
- Gustavo, Pedro, Álvares
- Gohan
- E outros...

**Veículos (2 registros):**
- DEF5678 - Chevrolet Opala Preto (Jose Antonio)
- ABC4321 - Chevrolet Marea Prata (Jose Antonio)

**Vagas (2 registros):**
- 001 - Disponível
- 002 - Disponível

**Histórico (7 registros):**
- Movimentação de entrada/saída de veículos
- Datas e horários

---



### 🔐 Autenticação (Públicos - Sem Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register/` | Registrar novo usuário |
| POST | `/auth/login/` | Fazer login |
| POST | `/auth/logout/` | Fazer logout |
| POST | `/auth/password-recovery/` | Solicitar recuperação de senha |
| PUT | `/auth/password-reset/` | Redefinir senha |

---

### 👥 Clientes (Requer Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/customers/` | Listar todos os clientes |
| GET | `/customers/<id>` | Obter cliente específico |
| POST | `/customers/` | Criar novo cliente |
| PUT | `/customers/<id>` | Atualizar cliente |
| DELETE | `/customers/<id>` | Deletar cliente |

---

### 🅿️ Vagas de Estacionamento (Requer Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/parking-spots/` | Listar todas as vagas |
| GET | `/parking-spots/<id>` | Obter vaga específica |
| POST | `/parking-spots/` | Criar nova vaga |
| PUT | `/parking-spots/<id>` | Atualizar vaga |
| DELETE | `/parking-spots/<id>` | Deletar vaga |

---

### 🚗 Tipos de Veículos (Requer Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/vehicle-types/` | Listar tipos de veículos |
| GET | `/vehicle-types/<id>` | Obter tipo específico |
| POST | `/vehicle-types/` | Criar novo tipo |
| PUT | `/vehicle-types/<id>` | Atualizar tipo |
| DELETE | `/vehicle-types/<id>` | Deletar tipo |

---

### 🚘 Veículos (Requer Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/vehicles/` | Listar todos os veículos |
| GET | `/vehicles/<id>` | Obter veículo específico |
| POST | `/vehicles/` | Registrar novo veículo |
| PUT | `/vehicles/<id>` | Atualizar veículo |
| DELETE | `/vehicles/<id>` | Deletar veículo |

---

### 📝 Registros de Estacionamento (Requer Login)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/parking-records/` | Listar registros |
| GET | `/parking-records/<id>` | Obter registro específico |
| POST | `/parking-records/` | Criar novo registro (entrada) |
| PUT | `/parking-records/<id>` | Atualizar registro (saída) |
| DELETE | `/parking-records/<id>` | Deletar registro |

---

## 🔒 Autenticação

### Como Funciona

1. **Registro**: Usuário fornece username, email e senha
2. **Login**: Credenciais são validadas, sessão criada
3. **Sessão**: ID de usuário armazenado na sessão Flask
4. **Proteção**: Decorator `@login_required` valida autenticação
5. **Logout**: Sessão é destruída

### Decorator @login_required

Todas as rotas de negócio (não-autenticação) são protegidas:

```python
from utils import login_required

@app.route('/customers/', methods=['GET'])
@login_required
def get_customers():
    # Apenas usuários autenticados podem acessar
    ...
```

### Resposta Sem Autenticação

```json
{
  "message": "Autenticação necessária. Faça login para acessar este recurso."
}
```

**Status HTTP**: `401 Unauthorized`

### Recuperação de Senha

1. POST `/auth/password-recovery/` com email
2. Código de 6 dígitos enviado via email
3. Válido por 15 minutos
4. Máximo 3 tentativas
5. PUT `/auth/password-reset/` com código e nova senha

---


## 🛠️ Troubleshooting

### Problema: Banco de dados vazio após importação
```
Solução:
1. Verifique se o arquivo db/parking_service_backup.sql existe
2. Execute: mysql -u root -p < db/parking_service_backup.sql
3. Confirme: mysql -u root -p -e "USE parking_service; SELECT COUNT(*) FROM auth_user;"
4. Se contar 1 usuários, está correto
5. Se nada aparecer, o arquivo SQL pode estar corrompido
```

### Problema: "ERROR 1049 (42000): Unknown database 'parking_service'"
```
Solução:
1. O backup deve criar o database automaticamente
2. Se não criar, crie manualmente: CREATE DATABASE parking_service;
3. Depois importe: mysql -u root -p parking_service < db/parking_service_backup.sql
```

### Problema: Erro ao fazer login com usuário de teste
```
Solução:
1. Verifique se o banco foi importado: SELECT * FROM auth_user;
2. Use exatamente: username="testejose" password="testejose"
3. Maiúsculas e minúsculas importam
4. Se nenhum usuário aparecer, importe o backup novamente
```

### Problema: "Connection refused" no banco de dados
```
Solução:
1. Verifique se MySQL está rodando
2. Verifique as credenciais em .env
3. Confirme que o banco 'parking_service' existe
```

### Problema: "Module not found: dotenv"
```
Solução:
pip install python-dotenv
```

### Problema: Não recebe email de recuperação de senha
```
Solução:
1. Verifique credenciais do Gmail em .env
2. Confirme que 2FA está habilitado
3. Use senha de aplicativo, não a senha principal
4. Verifique spam/lixo do email
```

### Problema: "Autenticação necessária" em todas as rotas
```
Solução:
1. Faça login primeiro em /auth/login/
2. Verifique se o cookie de sessão está sendo enviado
3. Confirme que @login_required está importado corretamente
```

---


### Padrão de Código

- Use Python 3.8+
- Siga PEP 8
- Adicione docstrings em funções
- Testes para novas funcionalidades

---

## 🔐 Segurança

### Boas Práticas Implementadas

✅ Credenciais em variáveis de ambiente  
✅ Autenticação obrigatória em rotas  
✅ Sessões seguras com Flask  
✅ Códigos de recuperação com expiração  
✅ Limite de tentativas em codes  
✅ Email para confirmação de ações sensíveis  

### Recomendações para Produção

- [ ] Implementar hash de senhas (bcrypt)
- [ ] Ativar HTTPS
- [ ] Implementar rate limiting
- [ ] Adicionar 2FA (autenticação de dois fatores)
- [ ] Usar Redis para armazenar códigos (não em memória)
- [ ] Implementar CORS adequadamente
- [ ] Adicionar logging completo
- [ ] Fazer backup automático do banco

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

Desenvolvido por José Antonio

**Data**: Maio de 2026

---