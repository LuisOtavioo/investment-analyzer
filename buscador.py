
import yfinance as yf

ativo = yf.Ticker("BBAS3.SA")

info = ativo.info

print(f"Empresa: {info['longName']}")
print(f"Preço atual: {info['currentPrice']}")
print(f"Variação de hoje: {info['regularMarketChangePercent']:.2f}%")