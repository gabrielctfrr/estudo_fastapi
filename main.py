from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

# 1. Importações do SQLModel
from sqlmodel import SQLModel, Field, create_engine, Session, select

# --- DEFINIÇÃO DO BANCO DE DADOS ---

# 2. Define o arquivo do banco de dados SQLite
sqlite_file_name = "database.db"
# A 'string de conexão'
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 3. Cria a 'engine', o motor que conecta ao banco
# O 'echo=True' é ótimo para aprender, pois mostra no terminal
# todos os comandos SQL que o Python está rodando por baixo dos panos.
engine = create_engine(sqlite_url, echo=True)

# 4. Função para criar as tabelas no banco
def create_db_and_tables():
    # SQLModel.metadata.create_all(engine) diz: "olhe todas as classes que
    # herdam de SQLModel e crie as tabelas no banco de dados 'engine'"
    SQLModel.metadata.create_all(engine)

# 5. Função para 'injetar' a sessão do banco em cada rota
# Isso é um 'Generator' do Python. É um padrão do FastAPI.
def get_session():
    # Abre uma nova conversa (sessão) com o banco
    with Session(engine) as session:
        yield session # Entrega a sessão para a rota

# --- FIM DA DEFINIÇÃO DO BANCO ---


# 6. Atualizando o modelo Aluno
# 'table=True' diz ao SQLModel para criar uma tabela chamada 'aluno'
# baseada nesta classe
class Aluno(SQLModel, table=True):
    # 'primary_key=True' define o 'id' como a coluna principal.
    # 'default=None' permite que o banco decida o ID (auto-incremento)
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    idade: int
    serie: str
    nota_media: float | None = Field(default=None) # Mudamos para Field

app = FastAPI()

# --- LÓGICA DA APLICAÇÃO ---

# 7. Evento de 'startup'
# Esta função roda UMA VEZ antes do servidor começar
@app.on_event("startup")
def on_startup():
    create_db_and_tables() # Cria as tabelas

@app.get("/")
def home():
    return {"mensagem": "API da Escola com Banco de Dados!"}

# 8. Reescrevendo as rotas CRUD

# O 'session: Session = Depends(get_session)' é a mágica.
# O FastAPI vai chamar a função get_session() e injetar a sessão
# do banco aqui para nós usarmos.
# 'Annotated' é a forma moderna de escrever isso.
SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/alunos")
def criar_aluno(aluno: Aluno, session: SessionDep):
    # Não usamos mais .append().
    # 1. Adiciona o objeto 'aluno' na sessão
    session.add(aluno)
    # 2. 'Comita' (salva) as mudanças no banco
    session.commit()
    # 3. Atualiza o objeto 'aluno' com os dados do banco (ex: o ID)
    session.refresh(aluno)
    return aluno

@app.get("/alunos")
def listar_alunos(session: SessionDep):
    # Não retornamos mais a lista.
    # Usamos session.exec() para executar uma query
    # 'select(Aluno)' é o mesmo que 'SELECT * FROM aluno'
    alunos = session.exec(select(Aluno)).all()
    return alunos

@app.get("/alunos/{id_aluno}")
def pegar_aluno_por_id(id_aluno: int, session: SessionDep):
    # session.get() é a forma mais rápida de buscar pela chave primária
    aluno = session.get(Aluno, id_aluno)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@app.put("/alunos/{id_aluno}")
def atualizar_aluno(id_aluno: int, aluno_atualizado: Aluno, session: SessionDep):
    aluno = session.get(Aluno, id_aluno)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Atualiza os dados do aluno que encontramos no banco
    # com os dados que recebemos (aluno_atualizado)
    aluno.nome = aluno_atualizado.nome
    aluno.idade = aluno_atualizado.idade
    aluno.serie = aluno_atualizado.serie
    aluno.nota_media = aluno_atualizado.nota_media

    session.add(aluno) # Adiciona o aluno atualizado à sessão
    session.commit() # Salva
    session.refresh(aluno) # Atualiza
    return aluno

@app.delete("/alunos/{id_aluno}")
def deletar_aluno(id_aluno: int, session: SessionDep):
    aluno = session.get(Aluno, id_aluno)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    session.delete(aluno) # Deleta o aluno
    session.commit() # Salva a deleção
    return {"mensagem": "Aluno deletado com sucesso!"}