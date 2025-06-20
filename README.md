

# Sistema de Monitoramento de Ônibus

Este é um **sistema completo para gerenciamento de frota de ônibus escolares**, incluindo:

- Rotas
- Motoristas
- Monitores
- Alunos
- Gestão Financeira

## Funcionalidades

- **Gerenciamento de Ônibus e suas características**
- **Controle de Rotas e Paradas**
- **Cadastro de Motoristas e Monitores**
- **Registro de Alunos por Parada**
- **Gestão Financeira:** Cálculo de custos diários, salários de motoristas e monitores, custo de combustível e outras despesas operacionais.

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)

## Instalação

1️⃣ **Clone o repositório:**

```bash
git clone https://github.com/FranciscoErik/transporteuniversitario.git
cd transporteuniversitario

2️⃣ Crie um ambiente virtual (opcional, mas fortemente recomendado):

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3️⃣ Instale as dependências:

pip install -r requirements.txt

4️⃣ Inicie o servidor:

python app.py

5️⃣ Acesse o aplicativo no navegador:

http://localhost:5000

Uso

Cadastro de Ônibus: Adicione informações como placa, modelo e eficiência de combustível.

Gerenciamento de Rotas: Associe paradas às rotas e depois associe as rotas ao ônibus.

Cadastro de Pessoal: Adicione motoristas e monitores e defina salários.

Gestão de Alunos: Cadastre os alunos nas paradas.

Gestão Financeira: Acompanhe gastos com combustível, salários e outras despesas.


Contribuição

Contribuição é sempre bem-vinda!
Se quiser dar uma ideia, reportar um bug ou fazer um pull
