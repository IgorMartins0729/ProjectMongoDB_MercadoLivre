"""Testes do CRUD do menu.py. Rode com: python -m unittest -v test_menu
Usa o banco 'mercadolivre_teste' (apagado ao final), nunca o 'mercadolivre' real."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

# menu.py roda o loop do menu ao ser importado: respondemos 'S' para ele sair na hora
with patch("builtins.input", return_value="S"), redirect_stdout(io.StringIO()):
    import menu

TEST_DB = "mercadolivre_teste"


def run(func, *args, inputs=()):
    """Executa uma função do menu simulando o teclado e devolve o que foi impresso."""
    out = io.StringIO()
    with patch("builtins.input", side_effect=list(inputs)), redirect_stdout(out):
        func(*args)
    return out.getvalue()


class TestCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu.db = menu.client[TEST_DB]

    @classmethod
    def tearDownClass(cls):
        menu.client.drop_database(TEST_DB)

    def setUp(self):
        menu.client.drop_database(TEST_DB)
        self.db = menu.db

    def test_conexao(self):
        self.assertEqual(menu.client.admin.command("ping")["ok"], 1)

    # ---------- Usuário ----------
    def test_usuario_create_com_dois_enderecos(self):
        run(menu.create_usuario, inputs=[
            "Ana", "Silva", "111",
            "Rua A", "1", "Centro", "SP", "SP", "01000", "S",
            "Rua B", "2", "Bairro", "RJ", "RJ", "20000", "N"])
        doc = self.db.usuario.find_one({"nome": "Ana"})
        self.assertEqual(doc["cpf"], "111")
        self.assertEqual([e["rua"] for e in doc["end"]], ["Rua A", "Rua B"])

    def test_usuario_read_lista_ordenada(self):
        self.db.usuario.insert_many([{"nome": "Zé", "cpf": "2"}, {"nome": "Ana", "cpf": "1"}])
        out = run(menu.read_usuario, "")
        self.assertLess(out.index("Ana"), out.index("Zé"))

    def test_usuario_update(self):
        self.db.usuario.insert_one({"nome": "Ana", "sobrenome": "Silva", "cpf": "1"})
        run(menu.update_usuario, "Ana", inputs=["Ana Maria", "", "999"])
        doc = self.db.usuario.find_one()
        self.assertEqual((doc["nome"], doc["sobrenome"], doc["cpf"]), ("Ana Maria", "Silva", "999"))

    def test_usuario_update_inexistente_nao_quebra(self):
        out = run(menu.update_usuario, "Ninguem")
        self.assertIn("não encontrado", out)

    def test_usuario_delete_por_nome_e_sobrenome(self):
        self.db.usuario.insert_many([{"nome": "Ana", "sobrenome": "Silva"},
                                     {"nome": "Ana", "sobrenome": "Souza"}])
        run(menu.delete_usuario, "Ana", "Silva")
        self.assertEqual([d["sobrenome"] for d in self.db.usuario.find()], ["Souza"])

    # ---------- Vendedor ----------
    def test_vendedor_crud(self):
        run(menu.create_vendedor, inputs=["João", "123", "Loja X"])
        self.assertIn("Loja X", run(menu.read_vendedor, ""))
        run(menu.update_vendedor, "João", inputs=["", "Loja Y"])
        self.assertEqual(self.db.vendedor.find_one()["loja"], "Loja Y")
        run(menu.delete_vendedor, "João")
        self.assertEqual(self.db.vendedor.count_documents({}), 0)

    def test_usuario_cpf_duplicado_recusado(self):
        self.db.usuario.insert_one({"nome": "Ana", "cpf": "111"})
        out = run(menu.create_usuario, inputs=["Outra", "Pessoa", "111"])
        self.assertIn("Já existe", out)
        self.assertEqual(self.db.usuario.count_documents({}), 1)

    # ---------- Produto (ligado ao vendedor pelo _id) ----------
    def test_produto_crud(self):
        vid = self.db.vendedor.insert_one({"nome": "João", "loja": "Loja X"}).inserted_id
        run(menu.create_produto, inputs=["Celular", "Bom", "1500", "1"])
        self.assertEqual(self.db.produto.find_one()["vendedor_id"], vid)
        self.assertIn("Loja X", run(menu.read_produto, ""))
        run(menu.update_produto, "Celular", inputs=["Smartphone", "1400"])
        doc = self.db.produto.find_one()
        self.assertEqual((doc["nome"], doc["preco"]), ("Smartphone", "1400"))
        self.assertIn("não encontrado", run(menu.update_produto, "Celular"))
        run(menu.delete_produto, "Smartphone")
        self.assertEqual(self.db.produto.count_documents({}), 0)

    def test_produto_sem_vendedor_recusado(self):
        run(menu.create_produto, inputs=["Celular", "Bom", "1500"])
        self.assertEqual(self.db.produto.count_documents({}), 0)

    # ---------- Compras e Favoritos (ligados a usuário e produto pelo _id) ----------
    def _base(self):
        uid = self.db.usuario.insert_one({"nome": "Vitória", "cpf": "123"}).inserted_id
        self.db.produto.insert_many([{"nome": "Banana"}, {"nome": "Maçã"}])  # lista: 1-Banana, 2-Maçã
        return uid

    def test_compra_crud(self):
        uid = self._base()
        run(menu.create_compra, inputs=["123", "2", "5"])
        doc = self.db.compras.find_one()
        maca = self.db.produto.find_one({"nome": "Maçã"})["_id"]
        self.assertEqual((doc["usuario_id"], doc["produto_id"], doc["quantidade"]), (uid, maca, "5"))
        self.assertNotIn("usuario", doc)  # só ids, sem nome/CPF repetido
        self.assertIn("Vitória - Maçã - Qtd: 5", run(menu.read_compra, "123"))
        run(menu.update_compra, inputs=["123", "1", "S", "1", "7"])
        self.assertIn("Vitória - Banana - Qtd: 7", run(menu.read_compra, ""))
        run(menu.delete_compra, inputs=["123", "1"])
        self.assertEqual(self.db.compras.count_documents({}), 0)

    def test_compra_cpf_inexistente_recusada(self):
        self._base()
        out = run(menu.create_compra, inputs=["999"])
        self.assertIn("não encontrado", out)
        self.assertEqual(self.db.compras.count_documents({}), 0)

    def test_compra_numero_invalido_recusada(self):
        self._base()
        out = run(menu.create_compra, inputs=["123", "9"])
        self.assertIn("inválida", out)
        self.assertEqual(self.db.compras.count_documents({}), 0)

    def test_compra_mostra_removido_se_produto_apagado(self):
        self._base()
        run(menu.create_compra, inputs=["123", "2", "1"])
        self.db.produto.delete_one({"nome": "Maçã"})
        self.assertIn("Vitória - (removido)", run(menu.read_compra, ""))

    def test_favorito_crud(self):
        uid = self._base()
        run(menu.create_favorito, inputs=["123", "2"])
        self.assertEqual(self.db.favoritos.find_one()["usuario_id"], uid)
        self.assertIn("Vitória - Maçã", run(menu.read_favorito, ""))
        run(menu.update_favorito, inputs=["123", "1", "1"])
        self.assertIn("Vitória - Banana", run(menu.read_favorito, "123"))
        run(menu.delete_favorito, inputs=["123", "1"])
        self.assertEqual(self.db.favoritos.count_documents({}), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
