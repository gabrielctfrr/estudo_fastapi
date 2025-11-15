from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

alunos_db = [] #Simulando uma base de dados com uma lista

class Aluno(BaseModel): #Definindo o modelo de dados do Aluno. Garante que os dados recebidos estejam nesse formato
    nome: str
    idade: int
    serie: str
    nota_media: float | None = None # Campo opcional (pode ser Nulo)

@app.get("/")
def home():
    return {"mensagem": "API da Escola rodando!"}

@app.get('/alunos')
def listar_alunos():
    return alunos_db

@app.post("/alunos/") # Criando a rota para cadastrar aluno. Usando aluno: Aluno, o FastAPI vai ler o JSON que enviarem e transformar nessa classe automaticamente.
def criar_aluno(aluno: Aluno):
    alunos_db.append(aluno) #Adicionando o aluno recebido na "base de dados"
    return {
        "mensagem": "Aluno cadastrado com sucesso!",
        "dados_recebidos": aluno
    }

@app.get("/alunos/{id_aluno}")
def pegar_aluno_por_id(id_aluno: int):
    try:
        aluno_encontrado = alunos_db[id_aluno]
        return aluno_encontrado
    except IndexError:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

@app.delete("/alunos/{id_aluno}")
def deletar_aluno(id_aluno: int):
    try:
        aluno_removido = alunos_db.pop(id_aluno)
        return {
            "mensagem": "Aluno removido com sucesso!",
            "aluno_removido": aluno_removido
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

@app.put("/alunos/{id_aluno}")
def atualizar_aluno(id_aluno: int, aluno_atualizado: Aluno):
    try:
        alunos_db[id_aluno] = aluno_atualizado
        return {
            "mensagem": "Aluno atualizado com sucesso!",
            "aluno_atualizado": aluno_atualizado
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")