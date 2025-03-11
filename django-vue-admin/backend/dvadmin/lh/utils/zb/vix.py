import numpy as np
import pandas as pd

# VIX计算函数
def calculate_vix(option_df_near, option_df_next, r, T1_days, T2_days):
    T1 = T1_days / 365
    T2 = T2_days / 365
    T30 = 30 / 365

    # 第一步: 计算远期价格F
    def forward_price(df, r, T):
        df['diff'] = np.abs(df['call'] - df['put'])
        K0_row = df.loc[df['diff'].idxmin()]
        K0 = K0_row['K']
        F = K0 + np.exp(r * T) * (K0_row['call'] - K0_row['put'])
        return F, K0

    F1, K0_1 = forward_price(option_df_near, r, T1)
    F2, K0_2 = forward_price(option_df_next, r, T2)

    # 第二步: 计算方差sigma^2
    def variance(df, F, K0, r, T):
        df = df.copy()
        df['delta_K'] = (df['K'].shift(-1) - df['K'].shift(1)) / 2
        df['delta_K'].iloc[0] = df['K'].iloc[1] - df['K'].iloc[0]
        df['delta_K'].iloc[-1] = df['K'].iloc[-1] - df['K'].iloc[-2]

        df['Q'] = np.where(df['K'] < K0, df['put'], np.where(df['K'] > K0, df['call'], (df['call'] + df['put']) / 2))

        term = df['delta_K'] / (df['K'] ** 2) * np.exp(r * T) * df['Q']
        sigma_sq = (2 / T) * term.sum() - (1 / T) * ((F / K0 - 1) ** 2)

        return sigma_sq

    sigma1_sq = variance(option_df_near, F1, K0_1, r, T1)
    sigma2_sq = variance(option_df_next, F2, K0_2, r, T2)

    # 第三步: 插值得到30天方差
    sigma30_sq = ((T2 - T30) / (T2 - T1)) * sigma1_sq + ((T30 - T1) / (T2 - T1)) * sigma2_sq

    # 第四步: 计算VIX
    VIX = 100 * np.sqrt(sigma30_sq)

    return VIX

# 示例数据结构（需要自行填入实际数据）
option_df_near = pd.DataFrame({
    'K': [2900, 2950, 3000, 3100, 3200, 3300, 3400, 3500],
    'call': [1.1081, 1.0669, 1.0065, 0.9138, 0.8172, 0.7194, 0.6187, 0.5194],
    'put': [0.0002, 0.0002, 0.0002, 0.00035, 0.00035, 0.00035, 0.0004, 0.0004]
})

option_df_next = pd.DataFrame({
    'K': [3600, 3700, 3800, 3900, 4000, 4100, 4200, 4300, 4400, 4500],
    'call': [0.4209, 0.3200, 0.2302, 0.1516, 0.0895, 0.0496, 0.0261, 0.0138, 0.0082, 0.0059],
    'put': [0.0026, 0.0058, 0.0130, 0.0338, 0.0725, 0.1311, 0.2076, 0.2952, 0.4084, 0.4992]
})

# 无风险利率（3%）和期限天数
r = 0.03
T1_days = 16
T2_days = 44

# 计算沪深300 VIX
vix_result = calculate_vix(option_df_near, option_df_next, r, T1_days, T2_days)

print("沪深300 VIX指数为:", vix_result)
