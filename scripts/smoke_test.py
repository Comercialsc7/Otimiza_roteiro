import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.loader import load_clientes, load_vendedores
from src.models.optimizer import otimizar_regiao
from src.viz.maps import construir_mapa

c = load_clientes("assets/amostras/clientes.csv")
v = load_vendedores("assets/amostras/vendedores.csv")
cli = c[c["regiao"] == "VALE"]
ven = v[v["regiao"] == "VALE"]
resultado, meta = otimizar_regiao(c, v, "VALE", n_pautas=2, limiar_km=40.0)
mapa = construir_mapa(cli, ven, resultado)
print("smoke_ok", len(resultado), meta["n_a_definir"], type(mapa).__name__)
