import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

CARTEIRA_CSV = "carteira.csv"
PASTA_RESULTADOS = "resultados"

# cria pasta de resultados se nao existir
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

# ---- carregamento ----

def carregar_carteira():
    if os.path.exists(CARTEIRA_CSV):
        return pd.read_csv(CARTEIRA_CSV)
    return pd.DataFrame(columns=["Ticker", "Quantidade", "Preco medio"])

def salvar_carteira(carteira):
    carteira.to_csv(CARTEIRA_CSV, index=False)

# ---- analise de ativo ----

def analisar_ativo(ticker):
    try:
        ativo = yf.Ticker(f"{ticker}.SA")
        info = ativo.info

        preco = info.get("currentPrice", 0)
        pvp = info.get("priceToBook", None)
        pl = info.get("trailingPE", None)
        dividendos = ativo.dividends

        if dividendos.empty or preco == 0:
            return None

        um_ano = pd.Timestamp.now(tz=dividendos.index.tz) - pd.DateOffset(years=1)
        div_anual = dividendos[dividendos.index >= um_ano].sum()
        dy = (div_anual / preco) * 100

        score_dy = min(dy / 12 * 4, 4)
        score_pvp = min((2 / pvp) * 3, 3) if pvp and pvp > 0 else 0
        pagamentos = len(dividendos[dividendos.index >= um_ano])
        score_consistencia = min(pagamentos / 12 * 3, 3)
        score = round(score_dy + score_pvp + score_consistencia, 2)

        return {
            "Ticker": ticker,
            "Preco": round(preco, 2),
            "DY (%)": round(dy, 2),
            "P/VP": round(pvp, 2) if pvp else "-",
            "P/L": round(pl, 2) if pl else "-",
            "Score": score
        }

    except Exception:
        return None

# ---- grafico historico ----

def exibir_grafico(ticker):
    print(f"\nBuscando historico de {ticker}...")

    ativo = yf.Ticker(f"{ticker}.SA")
    historico = ativo.history(period="1y")

    if historico.empty:
        print("Sem dados para exibir.")
        return

    datas = historico.index
    precos = historico["Close"]

    plt.figure(figsize=(12, 5))

    # linha de preco
    plt.plot(datas, precos, color="blue", linestyle="-", linewidth=2, label=f"{ticker} - Preco fechamento")

    # media movel 30 dias
    media_movel = precos.rolling(window=30).mean()
    plt.plot(datas, media_movel, color="red", linestyle="--", linewidth=1.5, label="Media movel 30 dias")

    plt.title(f"Historico de preco - {ticker} (ultimos 12 meses)")
    plt.xlabel("Data")
    plt.ylabel("Preco (R$)")
    plt.legend()
    plt.grid()

    # salvar ou nao
    salvar = input("\nSalvar grafico? [s/n]: ").strip().lower()
    if salvar == "s":
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        caminho = os.path.join(PASTA_RESULTADOS, f"grafico_{ticker}_{data_hoje}.pdf")
        plt.savefig(caminho)
        print(f"Grafico salvo em {caminho}")

    plt.show()

# ---- screener ----

def rodar_screener():
    ativos = [
        "BBAS3", "TAEE11", "EGIE3", "ITUB4", "VALE3", "VIVT3",
        "MXRF11", "HGLG11", "XPML11"
    ]

    print("\nAnalisando ativos...\n")
    resultados = []

    for ticker in ativos:
        dado = analisar_ativo(ticker)
        if dado:
            resultados.append(dado)
            print(f"OK | {ticker}")
        else:
            print(f"X  | {ticker} - sem dados suficientes")

    df = pd.DataFrame(resultados)
    df = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df.index += 1

    print("\nRANKING - Melhores ativos por score\n")
    print("=" * 60)
    print(df.to_string())

    # salva CSV com data
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    caminho_csv = os.path.join(PASTA_RESULTADOS, f"screener_{data_hoje}.csv")
    df.to_csv(caminho_csv, index=False)
    print(f"\nResultado salvo em {caminho_csv}")

    # opcao de ver grafico
    ver_grafico = input("\nVer grafico de algum ativo? (ex: BBAS3 ou enter para pular): ").upper().strip()
    if ver_grafico:
        exibir_grafico(ver_grafico)

# ---- carteira ----

def adicionar_compra():
    ticker = input("Ticker (ex: BBAS3): ").upper().strip()
    quantidade = int(input("Quantidade comprada: "))
    preco_pago = float(input("Preco pago por cota (R$): ").replace(",", "."))

    carteira = carregar_carteira()

    if ticker in carteira["Ticker"].values:
        idx = carteira.index[carteira["Ticker"] == ticker][0]
        qtd_atual = carteira.at[idx, "Quantidade"]
        preco_medio_atual = carteira.at[idx, "Preco medio"]

        novo_total = (qtd_atual * preco_medio_atual) + (quantidade * preco_pago)
        nova_quantidade = qtd_atual + quantidade
        novo_preco_medio = novo_total / nova_quantidade

        carteira.at[idx, "Quantidade"] = nova_quantidade
        carteira.at[idx, "Preco medio"] = round(novo_preco_medio, 2)

        print(f"\n{ticker} atualizado.")
        print(f"Quantidade total: {nova_quantidade}")
        print(f"Preco medio: R$ {novo_preco_medio:.2f}")
    else:
        nova_linha = pd.DataFrame([{
            "Ticker": ticker,
            "Quantidade": quantidade,
            "Preco medio": preco_pago
        }])
        carteira = pd.concat([carteira, nova_linha], ignore_index=True)
        print(f"\n{ticker} adicionado na carteira.")

    salvar_carteira(carteira)


def remover_ativo():
    carteira = carregar_carteira()

    if carteira.empty:
        print("\nCarteira vazia.")
        return

    print("\nAtivos na carteira:")
    for i, row in carteira.iterrows():
        print(f"  [{i}] {row['Ticker']} - {row['Quantidade']} cotas - preco medio R$ {row['Preco medio']}")

    try:
        idx = int(input("\nNumero do ativo: "))
        ticker = carteira.at[idx, "Ticker"]
        qtd_atual = carteira.at[idx, "Quantidade"]

        print(f"\n[1] Remover tudo ({qtd_atual} cotas)")
        print(f"[2] Remover parcial")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            carteira = carteira.drop(index=idx).reset_index(drop=True)
            print(f"\n{ticker} removido da carteira.")

        elif opcao == "2":
            qtd_remover = int(input(f"Quantas cotas remover? (max {qtd_atual}): "))
            if qtd_remover >= qtd_atual:
                carteira = carteira.drop(index=idx).reset_index(drop=True)
                print(f"\n{ticker} removido da carteira.")
            else:
                carteira.at[idx, "Quantidade"] = qtd_atual - qtd_remover
                print(f"\n{qtd_remover} cotas removidas. Restam {qtd_atual - qtd_remover} cotas de {ticker}.")

        salvar_carteira(carteira)

    except Exception:
        print("\nOpcao invalida.")


def analisar_carteira():
    carteira = carregar_carteira()

    if carteira.empty:
        print("\nCarteira vazia. Adicione ativos primeiro.")
        return

    print("\nAnalisando carteira...\n")
    resultados = []

    for _, linha in carteira.iterrows():
        ticker = linha["Ticker"]
        quantidade = linha["Quantidade"]
        preco_medio = linha["Preco medio"]

        dado = analisar_ativo(ticker)

        if dado:
            preco_atual = dado["Preco"]
            valor_investido = quantidade * preco_medio
            valor_atual = quantidade * preco_atual
            lucro = valor_atual - valor_investido
            lucro_pct = (lucro / valor_investido) * 100
            renda_mensal = (valor_atual * (dado["DY (%)"] / 100)) / 12

            resultados.append({
                "Ticker": ticker,
                "Qtd": quantidade,
                "P. medio": preco_medio,
                "P. atual": preco_atual,
                "Investido": round(valor_investido, 2),
                "Atual": round(valor_atual, 2),
                "Lucro/Prej.": round(lucro, 2),
                "Var. (%)": round(lucro_pct, 2),
                "Renda/mes": round(renda_mensal, 2)
            })
        else:
            print(f"X  | {ticker} - sem dados")

    df = pd.DataFrame(resultados)
    print(df.to_string(index=False))

    total_investido = df["Investido"].sum()
    total_atual = df["Atual"].sum()
    renda_total = df["Renda/mes"].sum()

    print("\n" + "=" * 50)
    print(f"Total investido:   R$ {total_investido:.2f}")
    print(f"Total atual:       R$ {total_atual:.2f}")
    print(f"Lucro/Prejuizo:    R$ {total_atual - total_investido:.2f}")
    print(f"Renda mensal est.: R$ {renda_total:.2f}")

# ---- menu ----

def menu():
    while True:
        print("\n=== Analisador de Investimentos ===")
        print("[1] Rodar screener")
        print("[2] Adicionar compra na carteira")
        print("[3] Remover ativo da carteira")
        print("[4] Analisar minha carteira")
        print("[0] Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            rodar_screener()
        elif opcao == "2":
            adicionar_compra()
        elif opcao == "3":
            remover_ativo()
        elif opcao == "4":
            analisar_carteira()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opcao invalida.")

if __name__ == "__main__":
    menu()