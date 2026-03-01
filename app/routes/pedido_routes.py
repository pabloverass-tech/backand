from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import pegar_sessao, verificar_token
from app.schemas.schemas import PedidoSchema, ItemPedidoSchema, RespondePedidosSchema
from app.models.models import Pedido, StatusPedido, Usuario, ItemPedido
from typing import List


pedidos_router = APIRouter(prefix="/pedidos", tags=["Pedidos"], dependencies=[Depends(verificar_token)])

@pedidos_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação
    """
    return {"mensagem": "Você acessou a rota de pedidos"}

@pedidos_router.post("/criar_pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """Cria um novo pedido."""
    novo_pedido = Pedido(usuario_id = pedido_schema.usuario_id)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso: ID {novo_pedido.id}"}

# O usuário pode cancelar apenas se for o DONO do pedido OU se for um ADMINISTRADOR.
@pedidos_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    
    # Busca o pedido no banco de dados usando o ID fornecido na URL
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    
     # Se o pedido não existir, lança um erro 400
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    
    # VERIFICAÇÃO DE AUTORIZAÇÃO (CRUCIAL)
    # A condição verifica: Se o usuário não é admin E não é o dono do pedido (compara o ID do usuário logado com o ID do dono do pedido)
    print(pedido.usuario_id)
    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=400, detail="você não tem autorização para fazer essa modificação")
    
     # Se passou na verificação, altera o status do pedido
    pedido.status = StatusPedido.CANCELADO
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }

@pedidos_router.get("/")
async def listar_pedidos(session: Session = Depends(pegar_sessao)):
    """Lista todos os pedidos."""
    pedidos = session.query(Pedido).all()
    return pedidos

@pedidos_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
        }

@pedidos_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, 
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, 
                             item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@pedidos_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

# Finalizar 1 pedido
@pedidos_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="você não tem autorização para fazer essa modificação")
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido
    }
    

# vizualizar 1 pedido
@pedidos_router.get("/pedido/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=400, detail="você não tem autorização para fazer essa modificação")
    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

# Vizualizar todos os pedidos de 1 usuário
@pedidos_router.get("/listar/pedidos-usuario", response_model=List[RespondePedidosSchema])
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
    return pedidos

# # Vizualizar todos os pedidos de 1 usuário
# @order_router.get("/listar/pedidos-usuario")
# async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
#     pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id)
#     return {
#         "pedidos": pedidos
#     }