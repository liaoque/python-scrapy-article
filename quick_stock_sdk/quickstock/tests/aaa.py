import akshare as ak
from quickstock import QuickStockClient

client = QuickStockClient()
stock_board_industry_name_em_df = ak.stock_board_industry_name_ths()
for index, row in stock_board_industry_name_em_df.iterrows():
    df_industry_stocks = client.industry_stocks(row["code"])
    print(f"行业包含 {len(df_industry_stocks)} 只股票")
    print(df_industry_stocks.head(10))
    break
    # print(row["行业名称"])
    # stock_board_industry_cons_em_df = ak.stock_board_industry_cons_em(symbol=row["行业名称"])
    # print(stock_board_industry_cons_em_df)
