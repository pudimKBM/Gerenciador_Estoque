from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, List, Optional
from passlib.context import CryptContext
from datetime import datetime, timezone  # Updated import
from typing import Dict, List, Optional

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
            movimentacao = Movimentacao(
                tipo="adicao",
                codigo_produto=codigo,
                quantidade=quantidade,
                data=datetime.now(timezone.utc),  # Updated
                usuario="Sistema"  # Pode ser ajustado para registrar o usuário
            )
            gerenciador_vendas.movimentacoes.append(movimentacao)
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

# Modelos Pydantic para vendas
class SaleItem(BaseModel):
    codigo: str
    quantidade: int
    preco_unitario: float
    desconto: Optional[float] = 0.0  # Em percentual

class VendaInput(BaseModel):
    items: List[SaleItem]
    desconto_total: Optional[float] = 0.0  # Desconto aplicado na venda inteira

class Venda(BaseModel):
    id_venda: int
    data: datetime
    itens: List[SaleItem]
    total: float
    desconto_total: float
    usuario: str

class Movimentacao(BaseModel):
    tipo: str  # 'adicao' ou 'remocao'
    codigo_produto: str
    quantidade: int
    data: datetime
    usuario: str

# Modelos Pydantic para promoções
class Promocao(BaseModel):
    codigo: str
    descricao: str
    desconto_percentual: float  # Percentual de desconto

# Instância do gerenciador de estoque
gerenciador = GerenciadorEstoque()

# Instância do gerenciador de vendas
class VendaInternal:
    def __init__(self, id_venda, data, itens, total, desconto_total, usuario):
        self.id_venda = id_venda
        self.data = data
        self.itens = itens
        self.total = total
        self.desconto_total = desconto_total
        self.usuario = usuario

class GerenciadorVendas:
    def __init__(self):
        self.vendas: List[VendaInternal] = []
        self.movimentacoes: List[Movimentacao] = []
        self.proximo_id = 1

    def registrar_venda(self, venda_input: VendaInput, usuario: str):
        total = 0.0
        for item in venda_input.items:
            produto = gerenciador.estoque.get(item.codigo)
            if not produto:
                raise ValueError(f"Produto com código {item.codigo} não encontrado.")
            if produto.quantidade < item.quantidade:
                raise ValueError(f"Estoque insuficiente para o produto {produto.nome}.")
            # Calcula o total com desconto
            total += item.quantidade * produto.preco * (1 - item.desconto / 100)
        
        # Aplica desconto total
        total *= (1 - venda_input.desconto_total / 100)

        # Atualiza o estoque e registra movimentações
        for item in venda_input.items:
            gerenciador.remover_estoque(item.codigo, item.quantidade)
            movimentacao = Movimentacao(
                tipo="remocao",
                codigo_produto=item.codigo,
                quantidade=item.quantidade,
                data=datetime.now(timezone.utc),  # Updated
                usuario=usuario
            )
            self.movimentacoes.append(movimentacao)
        
        venda = VendaInternal(
            id_venda=self.proximo_id,
            data=datetime.now(timezone.utc),  # Updated
            itens=venda_input.items,
            total=total,
            desconto_total=venda_input.desconto_total,
            usuario=usuario
        )
        self.vendas.append(venda)
        self.proximo_id += 1
        return venda

    def gerar_recibo(self, id_venda: int) -> Dict:
        venda = next((v for v in self.vendas if v.id_venda == id_venda), None)
        if not venda:
            raise ValueError("Venda não encontrada.")
        
        recibo = {
            "id_venda": venda.id_venda,
            "data": venda.data,
            "usuario": venda.usuario,
            "itens": [
                {
                    "codigo": item.codigo,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario,
                    "desconto": item.desconto,
                    "subtotal": round(item.quantidade * item.preco_unitario * (1 - item.desconto / 100), 2)
                }
                for item in venda.itens
            ],
            "desconto_total": venda.desconto_total,
            "total": round(venda.total, 2)
        }
        return recibo

    def relatorio_vendas(self):
        return self.vendas

    def relatorio_movimentacoes(self):
        return self.movimentacoes

gerenciador_vendas = GerenciadorVendas()

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

# Banco de dados de promoções
promocoes_db: Dict[str, Promocao] = {}

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
    user_in_db = UsuarioInDB(**usuario.model_dump(), hashed_password=hashed_password)
    usuarios_db[usuario.username] = user_in_db
    return user_in_db

# Endpoint para listar todos os usuários (apenas para fins de administração)
@app.get("/usuarios/", response_model=List[Usuario])
async def list_users(current_user: UsuarioInDB = Depends(get_current_user)):
    return list(usuarios_db.values())

# Endpoint para cadastrar produtos (apenas para usuários autenticados)
@app.post("/produtos/")
async def cadastrar_produto(produto: ProdutoInput, current_user: UsuarioInDB = Depends(get_current_user)):
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
        # Registrar movimentação de adição ao estoque
        movimentacao = Movimentacao(
            tipo="adicao",
            codigo_produto=produto.codigo,
            quantidade=produto.quantidade,
            data=datetime.now(timezone.utc),  # Updated
            usuario=current_user.username
        )
        gerenciador_vendas.movimentacoes.append(movimentacao)
        return novo_produto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para adicionar ao estoque
@app.put("/produtos/{codigo}/adicionar")
async def adicionar_estoque(codigo: str, quantidade: int, current_user: UsuarioInDB = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.adicionar_estoque(codigo, quantidade)
        # Registrar movimentação de adição
        movimentacao = Movimentacao(
            tipo="adicao",
            codigo_produto=codigo,
            quantidade=quantidade,
            data=datetime.now(timezone.utc),  # Updated
            usuario=current_user.username
        )
        gerenciador_vendas.movimentacoes.append(movimentacao)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para remover do estoque
@app.put("/produtos/{codigo}/remover")
async def remover_estoque(codigo: str, quantidade: int, current_user: UsuarioInDB = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.remover_estoque(codigo, quantidade)
        # Registrar movimentação de remoção
        movimentacao = Movimentacao(
            tipo="remocao",
            codigo_produto=codigo,
            quantidade=quantidade,
            data=datetime.now(timezone.utc),  # Updated
            usuario=current_user.username
        )
        gerenciador_vendas.movimentacoes.append(movimentacao)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para atualizar o estoque
@app.put("/produtos/{codigo}/atualizar")
async def atualizar_estoque(codigo: str, quantidade: int, current_user: UsuarioInDB = Depends(get_current_user)):
    try:
        produto_atualizado = gerenciador.atualizar_estoque(codigo, quantidade)
        # Registrar movimentação de atualização
        movimentacao = Movimentacao(
            tipo="atualizacao",
            codigo_produto=codigo,
            quantidade=quantidade,
            data=datetime.now(timezone.utc),  # Updated
            usuario=current_user.username
        )
        gerenciador_vendas.movimentacoes.append(movimentacao)
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para alerta de estoque baixo
@app.get("/produtos/alerta")
async def alerta_estoque_baixo(current_user: UsuarioInDB = Depends(get_current_user)):
    alerta = gerenciador.alerta_estoque_baixo()
    return alerta

# Endpoint para registrar uma venda
@app.post("/vendas/")
async def registrar_venda(venda: VendaInput, current_user: UsuarioInDB = Depends(get_current_user)):
    try:
        # Atualizar preços com base no estoque atual
        for item in venda.items:
            produto = gerenciador.estoque.get(item.codigo)
            if produto:
                item.preco_unitario = produto.preco
        nova_venda = gerenciador_vendas.registrar_venda(venda, current_user.username)
        recibo = gerenciador_vendas.gerar_recibo(nova_venda.id_venda)
        return recibo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para gerar relatório de vendas
@app.get("/relatorios/vendas/")
async def relatorio_vendas(current_user: UsuarioInDB = Depends(get_current_user)):
    vendas = gerenciador_vendas.relatorio_vendas()
    return vendas

# Endpoint para gerar relatório de estoque
@app.get("/relatorios/estoque/")
async def relatorio_estoque(current_user: UsuarioInDB = Depends(get_current_user)):
    return gerenciador.estoque

# Endpoint para gerar histórico de movimentações
@app.get("/relatorios/movimentacoes/")
async def relatorio_movimentacoes(current_user: UsuarioInDB = Depends(get_current_user)):
    movimentacoes = gerenciador_vendas.relatorio_movimentacoes()
    return movimentacoes

# Endpoints para gerenciar promoções
@app.post("/promocoes/")
async def criar_promocao(promocao: Promocao, current_user: UsuarioInDB = Depends(get_current_user)):
    if promocao.codigo in promocoes_db:
        raise HTTPException(status_code=400, detail="Código de promoção já existe.")
    promocoes_db[promocao.codigo] = promocao
    return promocao

@app.get("/promocoes/")
async def listar_promocoes(current_user: UsuarioInDB = Depends(get_current_user)):
    return list(promocoes_db.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
