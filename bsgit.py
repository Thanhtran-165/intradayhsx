import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from vnstock import Vnstock
import time
import warnings

# Tắt cảnh báo không cần thiết
warnings.filterwarnings("ignore")

def format_currency(value):
    """Định dạng số tiền với dấu chấm phân tách hàng nghìn"""
    return "{:,.0f}".format(value).replace(",", ".")

def analyze_stock(symbol):
    """Phân tích chi tiết mã cổ phiếu với cơ chế retry và hiển thị chuyên nghiệp"""
    try:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Lấy dữ liệu từ API
                stock = Vnstock().stock(symbol=symbol, source='TCBS')
                data = stock.quote.intraday(symbol=symbol, page_size=10_000, show_log=False)
                
                # Kiểm tra dữ liệu hợp lệ
                if data.empty:
                    raise ValueError(f"Dữ liệu trống cho mã {symbol}. Mã có thể không tồn tại hoặc chưa có giao dịch.")
                
                # Xử lý dữ liệu
                df = data.copy()
                df['time'] = pd.to_datetime(df['time'])
                
                # Chuyển đổi múi giờ sang UTC
                if df['time'].dt.tz is not None:
                    df['time'] = df['time'].dt.tz_convert('UTC').dt.tz_localize(None)
                
                df['value'] = df['price'] * df['volume']
                df['in_flow'] = np.where(df['match_type'] == 'Buy', df['value'], 0)
                df['out_flow'] = np.where(df['match_type'] == 'Sell', df['value'], 0)
                
                # Tổng hợp theo phút
                df.set_index('time', inplace=True)
                resampled = df.resample('min').agg({
                    'in_flow': 'sum',
                    'out_flow': 'sum',
                    'volume': 'sum',
                    'match_type': 'count'
                }).rename(columns={'match_type': 'order_count'})
                
                resampled['net_flow'] = resampled['in_flow'] - resampled['out_flow']
                resampled['cum_net_flow'] = resampled['net_flow'].cumsum()
                resampled['buy_count'] = df[df['match_type'] == 'Buy'].resample('min')['match_type'].count()
                resampled['sell_count'] = df[df['match_type'] == 'Sell'].resample('min')['match_type'].count()
                resampled['cum_buy'] = resampled['buy_count'].cumsum()
                resampled['cum_sell'] = resampled['sell_count'].cumsum()
                resampled['cum_in_flow'] = resampled['in_flow'].cumsum()
                resampled['cum_out_flow'] = resampled['out_flow'].cumsum()

                # Tính toán khối lượng trung bình của lệnh mua và bán
                resampled['avg_buy_volume'] = np.where(resampled['buy_count'] != 0, 
                                                       df[df['match_type'] == 'Buy'].resample('min')['volume'].sum() / resampled['buy_count'], 
                                                       0)
                resampled['avg_sell_volume'] = np.where(resampled['sell_count'] != 0, 
                                                        df[df['match_type'] == 'Sell'].resample('min')['volume'].sum() / resampled['sell_count'], 
                                                        0)
                # Tính tỷ lệ khối lượng trung bình lệnh mua/bán
                resampled['avg_buy_sell_ratio'] = np.where(resampled['avg_sell_volume'] != 0, 
                                                           resampled['avg_buy_volume'] / resampled['avg_sell_volume'], 
                                                           np.inf)

                # Tính toán các chỉ số phân tích
                volatility = df['price'].std()
                imbalance_ratio = np.where(resampled['out_flow'] != 0, resampled['in_flow'] / resampled['out_flow'], 0)
                order_to_volume_ratio = np.where(resampled['volume'] != 0, resampled['order_count'] / resampled['volume'], 0)

                # Phần tóm tắt với định dạng tiền tệ có dấu chấm
                summary = {
                    'Tổng dòng tiền vào (VND)': format_currency(resampled['in_flow'].sum()),
                    'Tổng dòng tiền ra (VND)': format_currency(resampled['out_flow'].sum()),
                    'Dòng tiền ròng (VND)': format_currency(resampled['net_flow'].sum()),
                    'Tổng số lệnh mua': int(resampled['buy_count'].sum()),
                    'Tổng số lệnh bán': int(resampled['sell_count'].sum()),
                    'Khối lượng trung bình lệnh mua': resampled['avg_buy_volume'].mean(),
                    'Khối lượng trung bình lệnh bán': resampled['avg_sell_volume'].mean(),
                    'Tỷ lệ khối lượng trung bình mua/bán': resampled['avg_buy_sell_ratio'].replace(np.inf, 0).mean(),
                    'Giá cao nhất': df['price'].max(),
                    'Giá thấp nhất': df['price'].min(),
                    'Giá trung bình': df['price'].mean(),
                    'Volatility (Độ lệch chuẩn giá)': volatility,
                    'Imbalance Ratio (Trung bình)': np.mean(imbalance_ratio),
                    'Order-to-Volume Ratio (Trung bình)': np.mean(order_to_volume_ratio)
                }

                # Hiển thị phần tóm tắt
                print("\n=== TÓM TẮT PHÂN TÍCH ===")
                for key, value in summary.items():
                    if isinstance(value, str):
                        print(f"{key}: {value}")
                    elif isinstance(value, float):
                        print(f"{key}: {value:.6f}")
                    else:
                        print(f"{key}: {value}")
                print("=========================\n")

                # Cấu hình kiểu chữ toàn cục với kích thước nhỏ hơn
                plt.rcParams.update({
                    'font.size': 8,          # Kích thước chữ chung
                    'axes.titlesize': 10,    # Kích thước tiêu đề trục
                    'axes.labelsize': 9,     # Kích thước nhãn trục
                    'xtick.labelsize': 7,    # Kích thước chữ trên trục x
                    'ytick.labelsize': 7,    # Kích thước chữ trên trục y
                    'legend.fontsize': 8,    # Kích thước chữ chú thích
                    'figure.titlesize': 12   # Kích thước tiêu đề biểu đồ
                })

                # 1. Biểu đồ dòng tiền ròng lũy kế (riêng biệt) với chú thích IQR
                plt.figure(figsize=(12, 6), constrained_layout=True)
                plt.plot(resampled.index, resampled['cum_net_flow'], 
                        label='Dòng tiền ròng', color='purple', linewidth=2)
                plt.title(f'BIỂU ĐỒ DÒNG TIỀN RÒNG LŨY KẾ - {symbol}', fontsize=12, pad=20)
                plt.xlabel('Thời gian', fontsize=9)
                plt.ylabel('VND', fontsize=9)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.legend(loc='upper left', fontsize=8, bbox_to_anchor=(0, 1.1))
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.xticks(rotation=45, fontsize=7)
                plt.yticks(fontsize=7)

                # Phát hiện đột biến bằng IQR
                Q1 = resampled['net_flow'].quantile(0.25)
                Q3 = resampled['net_flow'].quantile(0.75)
                IQR = Q3 - Q1
                outliers = resampled[(resampled['net_flow'] > Q3 + 1.5 * IQR) | 
                                    (resampled['net_flow'] < Q1 - 1.5 * IQR)]
                
                # Chú thích các điểm đột biến
                for _, row in outliers.iterrows():
                    plt.annotate(f"{format_currency(row['net_flow'])} VND", 
                                (row.name, row['cum_net_flow']),
                                xytext=(0, 10), textcoords='offset points',
                                ha='center', fontsize=7,
                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
                plt.show()

                # 2. Biểu đồ tỷ lệ khối lượng trung bình lệnh mua/bán
                plt.figure(figsize=(12, 6), constrained_layout=True)
                plt.plot(resampled.index, resampled['avg_buy_sell_ratio'], 
                         label='Tỷ lệ khối lượng TB mua/bán', color='blue', linewidth=2)
                plt.axhline(y=1, color='gray', linestyle='--', alpha=0.7, label='Tỷ lệ cân bằng (1)')
                plt.title(f'TỶ LỆ KHỐI LƯỢNG TRUNG BÌNH MUA/BÁN THEO THỜI GIAN - {symbol}', fontsize=12, pad=20)
                plt.xlabel('Thời gian', fontsize=9)
                plt.ylabel('Tỷ lệ (Mua/Bán)', fontsize=9)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.legend(loc='upper left', fontsize=8, bbox_to_anchor=(0, 1.1))
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.xticks(rotation=45, fontsize=7)
                plt.yticks(fontsize=7)
                plt.show()

                # 3. Biểu đồ dòng tiền mua/bán lũy kế
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
                
                ax1.plot(resampled.index, resampled['cum_in_flow'], 
                        label='Tổng dòng tiền mua', color='green', linewidth=2)
                ax1.set_title(f'DÒNG TIỀN MUA LŨY KẾ - {symbol}', fontsize=10, pad=15)
                ax1.set_xlabel('Thời gian', fontsize=9)
                ax1.set_ylabel('VND', fontsize=9)
                ax1.grid(True, linestyle='--', alpha=0.7)
                ax1.legend(loc='upper left', fontsize=8, bbox_to_anchor=(0, 1.1))
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax1.tick_params(axis='both', labelsize=7)

                ax2.plot(resampled.index, resampled['cum_out_flow'], 
                        label='Tổng dòng tiền bán', color='red', linewidth=2)
                ax2.set_title(f'DÒNG TIỀN BÁN LŨY KẾ - {symbol}', fontsize=10, pad=15)
                ax2.set_xlabel('Thời gian', fontsize=9)
                ax2.set_ylabel('VND', fontsize=9)
                ax2.grid(True, linestyle='--', alpha=0.7)
                ax2.legend(loc='upper left', fontsize=8, bbox_to_anchor=(0, 1.1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax2.tick_params(axis='both', labelsize=7)

                plt.suptitle('DÒNG TIỀN MUA/BÁN LŨY KẾ THEO THỜI GIAN', fontsize=12, y=1.02)
                plt.show()

                # 4. Heatmap áp lực mua/bán kết hợp (dòng tiền ròng) với bảng màu coolwarm
                df_heatmap = df.reset_index()
                df_heatmap['time'] = df_heatmap['time'].dt.strftime('%H:%M')  # Chỉ hiển thị giờ và phút
                df_heatmap['price'] = df_heatmap['price'].round(2)
                
                # Tính net_flow = in_flow - out_flow
                df_heatmap['net_flow'] = df_heatmap['in_flow'] - df_heatmap['out_flow']
                
                # Pivot table cho net_flow
                net_flow_pivot = df_heatmap.pivot_table(index='time', columns='price', values='net_flow', aggfunc='sum', fill_value=0)
                
                # Định dạng giá trị về triệu VND
                net_flow_pivot_million = net_flow_pivot / 1_000_000  # Chuyển sang triệu VND
                
                # Vẽ heatmap với bảng màu coolwarm
                plt.figure(figsize=(10, 6), constrained_layout=True)
                sns.heatmap(
                    net_flow_pivot_million,
                    cmap='coolwarm',  # Bảng màu: xanh dương (âm) -> đỏ (dương)
                    center=0,
                    annot=False,  # Không hiển thị giá trị số trên heatmap
                    cbar_kws={'label': 'Net Flow (Triệu VND)'}
                )
                plt.title(f'Heatmap Áp Lực Mua/Bán (Dòng Tiền Ròng) - {symbol}', fontsize=12)
                plt.xlabel('Giá', fontsize=9)
                plt.ylabel('Thời Gian (HH:MM)', fontsize=9)
                plt.show()

                # 5. Các biểu đồ còn lại trong lưới
                fig = plt.figure(figsize=(16, 20), constrained_layout=False)
                gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], hspace=0.4, wspace=0.3)
                
                # Biểu đồ khối lượng giao dịch
                ax = fig.add_subplot(gs[0, 0])
                ax.plot(resampled.index, resampled['volume'], 
                        label='Khối lượng giao dịch', color='blue', linewidth=2)
                ax.set_title('KHỐI LƯỢNG GIAO DỊCH THEO THỜI GIAN', fontsize=10, pad=10)
                ax.set_xlabel('Thời gian', fontsize=9)
                ax.set_ylabel('Khối lượng', fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend(fontsize=8, loc='upper right')
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax.tick_params(axis='both', labelsize=7)
                ax.tick_params(axis='x', rotation=45)

                # Biểu đồ áp lực mua/bán
                ax = fig.add_subplot(gs[0, 1])
                ax.bar(resampled.index, resampled['in_flow'], width=0.001, 
                      label='Áp lực mua', color='green')
                ax.bar(resampled.index, -resampled['out_flow'], width=0.001, 
                      label='Áp lực bán', color='red')
                ax.set_title('ÁP LỰC MUA/BÁN', fontsize=10, pad=10)
                ax.set_xlabel('Thời gian', fontsize=9)
                ax.set_ylabel('VND', fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend(fontsize=8, loc='upper right')
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax.tick_params(axis='both', labelsize=7)
                ax.tick_params(axis='x', rotation=45)

                # Biểu đồ số lệnh lũy kế
                ax = fig.add_subplot(gs[1, 0])
                ax.plot(resampled.index, resampled['cum_buy'], label='Lệnh mua', color='green')
                ax.plot(resampled.index, resampled['cum_sell'], label='Lệnh bán', color='red')
                ax.set_title('SỐ LỆNH MUA/BÁN LŨY KẾ', fontsize=10, pad=10)
                ax.set_xlabel('Thời gian', fontsize=9)
                ax.set_ylabel('Số lượng lệnh', fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend(fontsize=8, loc='upper right')
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax.tick_params(axis='both', labelsize=7)
                ax.tick_params(axis='x', rotation=45)

                # Phân bố số lệnh theo giá
                ax = fig.add_subplot(gs[1, 1])
                sns.histplot(data=df[df['match_type']=='Buy'], x='price', 
                            bins=30, color='green', label='Lệnh mua', alpha=0.5, 
                            kde=True, ax=ax, stat='count')
                sns.histplot(data=df[df['match_type']=='Sell'], x='price', 
                            bins=30, color='red', label='Lệnh bán', alpha=0.5, 
                            kde=True, ax=ax, stat='count')
                ax.set_title('PHÂN BỐ SỐ LỆNH THEO GIÁ', fontsize=10, pad=10)
                ax.set_xlabel('Giá', fontsize=9)
                ax.set_ylabel('Số lượng lệnh', fontsize=9)
                ax.legend(fontsize=8)
                ax.tick_params(axis='both', labelsize=7)

                # Phân bố khối lượng theo giá
                ax = fig.add_subplot(gs[2, 0])
                sns.histplot(data=df, x='price', weights='volume', 
                            bins=30, kde=True, color='blue', ax=ax)
                ax.set_title('PHÂN BỐ KHỐI LƯỢNG THEO GIÁ', fontsize=10, pad=10)
                ax.set_xlabel('Giá', fontsize=9)
                ax.set_ylabel('Khối lượng', fontsize=9)
                ax.tick_params(axis='both', labelsize=7)

                # Phân bố dòng tiền theo giá
                ax = fig.add_subplot(gs[2, 1])
                sns.histplot(data=df[df['match_type']=='Buy'], x='price', 
                            weights='in_flow', bins=30, color='green', 
                            label='Dòng vào', alpha=0.5, kde=True, ax=ax)
                sns.histplot(data=df[df['match_type']=='Sell'], x='price', 
                            weights='out_flow', bins=30, color='red', 
                            label='Dòng ra', alpha=0.5, kde=True, ax=ax)
                ax.set_title('PHÂN BỐ DÒNG TIỀN THEO GIÁ', fontsize=10, pad=10)
                ax.set_xlabel('Giá', fontsize=9)
                ax.set_ylabel('VND', fontsize=9)
                ax.legend(fontsize=8)
                ax.tick_params(axis='both', labelsize=7)

                plt.suptitle(f'PHÂN TÍCH CHI TIẾT MÃ CỔ PHIẾU: {symbol}', fontsize=14, y=0.95)
                plt.show()
                
                break
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Lỗi '{e}' khi lấy dữ liệu cho mã {symbol}. Thử lại lần {attempt + 2} sau {2 ** attempt} giây...")
                    time.sleep(2 ** attempt)
                else:
                    print(f"Không thể lấy dữ liệu cho mã {symbol} sau {max_retries} lần thử.")
                    
    except Exception as e:
        print(f"Lỗi phân tích mã {symbol}: {str(e)}")

def main():
    print("=== HỆ THỐNG PHÂN TÍCH CỔ PHIẾU ===")
    print("Hướng dẫn:")
    print("- Nhập mã cổ phiếu (ví dụ: ACB, VIC, VNM...) để xem phân tích")
    print("- Gõ END để kết thúc phiên làm việc")
    print("==================================")
    
    while True:
        symbol = input("\nNhập mã cổ phiếu để xem (gõ END để kết thúc): ").strip().upper()
        if symbol == 'END':
            print("Kết thúc phiên làm việc. Tạm biệt!")
            break
        if not symbol:
            print("Vui lòng nhập mã cổ phiếu!")
            continue
        print(f"Đang tải dữ liệu cho mã {symbol}... Vui lòng chờ...")
        analyze_stock(symbol)

if __name__ == "__main__":
    main()