from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, List, Optional
from passlib.context import CryptContext

app = FastAPI()

# Classes fornecidas
class Produto:
    def __init__(self, nome, codigo, categoria, quantidade, preco, descricao, fornecedor):
        self.nome = nome
        self.codigo = codigo
        self.categoria = categoria
        self.quantidade = quantidade
        self.preco = preco
        self.descricao = descricao
        self.fornecedor = fornecedor

    def __str__(self):
        return f"{self.nome} ({self.codigo}) - {self.quantidade} unidades em estoque"


class GerenciadorEstoque:
    def __init__(self):
        self.estoque = {}

    def cadastrar_produto(self, nome, codigo, categoria, quantidade, preco, descricao, fornecedor):
        if codigo in self.estoque:
            raise ValueError("Código de produto já existe")
        produto = Produto(nome, codigo, categoria, quantidade, preco, descricao, fornecedor)
        self.estoque[codigo] = produto
        return produto

    def adicionar_estoque(self, codigo, quantidade):
        if codigo in self.estoque:
            self.estoque[codigo].quantidade += quantidade
            return self.estoque[codigo]
        else:
            raise ValueError("Produto não encontrado")

    def remover_estoque(self, codigo, quantidade):
        if codigo in self.estoque:
            if quantidade <= self.estoque[codigo].quantidade:
                self.estoque[codigo].quantidade -= quantidade
                return self.estoque[codigo]
            else:
                raise ValueError("Quantidade a remover excede o estoque disponível")
        else:
            raise ValueError("Produto não encontrado")

    def atualizar_estoque(self, codigo, quantidade):
        if codigo in self.estoque:
            self.estoque[codigo].quantidade = quantidade
            return self.estoque[codigo]
        else:
            raise ValueError("Produto não encontrado")

    def alerta_estoque_baixo(self):
        return {codigo: produto for codigo, produto in self.estoque.items() if produto.quantidade < 5}

# Modelos Pydantic para validação de entrada de dados
class ProdutoInput(BaseModel):
    nome: str
    codigo: str
    categoria: str
    quantidade: int
    preco: float
    descricao: str
    fornecedor: str

# Modelos Pydantic para usuários
class Usuario(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = False

class UsuarioCreate(Usuario):
    password: str

class UsuarioInDB(Usuario):
    hashed_password: str

# Instância do gerenciador de estoque
gerenciador = GerenciadorEstoque()

# Simulação de banco de dados de usuários
usuarios_db: Dict[str, UsuarioInDB] = {
    "user1": UsuarioInDB(
        username="user1",
        full_name="User One",
        email="user1@example.com",
        hashed_password="$2b$12$KixcHxlOe.YmVfXH5tBZjeIjsuSZxThmFfXuzYvhP5gQab7sVXvXO",  # senha: "secret"
        disabled=False,
    )
}

# Configuração de criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para gerar hash da senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Função para verificar senha
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Função para autenticar usuário
def authenticate_user(username: str, password: str) -> Optional[UsuarioInDB]:
    user = usuarios_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# Esquema OAuth2 para autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

# Dependência para autenticação
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UsuarioInDB:
    user = usuarios_db.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Endpoint para criar um novo usuário
@app.post("/usuarios/", response_model=Usuario)
async def create_user(usuario: UsuarioCreate):
    if usuario.username in usuarios_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = hash_password(usuario.password)
    user_in_db = UsuarioInDB(**usuario.dict(), hashed_password=hashed_password)
    usuarios_db[usuario.username] = user_in_db
    return user_in_db

# Endpoint para listar todos os usuários (apenas para fins de administração)
@app.get("/usuarios/", response_model=List[Usuario])
async def list_users(current_user: UsuarioInDB = Depends(get_current_user)):
    return list(usuarios_db.values())

# Endpoint para cadastrar produtos (apenas para usuários autenticados)
@app.post("/produtos/")
async def cadastrar_produto(produto: ProdutoInput, user: dict = Depends(get_current_user)):
    try:
        novo_produto = gerenciador.cadastrar_produto(
            nome=produto.nome,
            codigo=produto.codigo,
            categoria=produto.categoria,
            quantidade=produto.quantidade,
            preco=produto.preco,
            descricao=produto.descricao,
            fornecedor=produto.fornecedor
        )
        return novo_produto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para adicionar ao estoque
@app.put("/produtos/{codigo}/adicionar")
async def adicionar_estoque(codigo: str, quantidade: int, user: dict = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.adicionar_estoque(codigo, quantidade)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para remover do estoque
@app.put("/produtos/{codigo}/remover")
async def remover_estoque(codigo: str, quantidade: int, user: dict = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.remover_estoque(codigo, quantidade)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para atualizar o estoque
@app.put("/produtos/{codigo}/atualizar")
async def atualizar_estoque(codigo: str, quantidade: int, user: dict = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.atualizar_estoque(codigo, quantidade)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para alerta de estoque baixo
@app.get("/produtos/alerta")
async def alerta_estoque_baixo(user: dict = Depends(get_current_user)):
    alerta = gerenciador.alerta_estoque_baixo()
    return alerta

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
