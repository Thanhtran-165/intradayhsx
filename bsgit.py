import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading
import time
from vnstock import Vnstock

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Theo dõi giá Intraday")
        self.running = False
        self.symbol = tk.StringVar(value="ACB")
        self.interval = tk.StringVar(value="1p")
        self.intraday_data = None
        self.create_widgets()

    def create_widgets(self):
        # Frame cài đặt
        input_frame = ttk.LabelFrame(self.root, text="Cài đặt", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        tk.Label(input_frame, text="Mã cổ phiếu:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        symbol_combo = ttk.Combobox(input_frame, textvariable=self.symbol)
        symbol_combo['values'] = ['ACB', 'VCB', 'BID', 'FPT']
        symbol_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Label(input_frame, text="Khoảng thời gian:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        interval_combo = ttk.Combobox(input_frame, textvariable=self.interval)
        interval_combo['values'] = ['1s', '5s', '10s', '15s', '30s', '1p', '5p', '10p', '15p']
        interval_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.start_button = tk.Button(input_frame, text="Bắt đầu", command=self.toggle_monitoring, bg="green", fg="white")
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame thống kê theo giá
        price_frame = ttk.LabelFrame(self.root, text="Thống kê theo giá", padding=10)
        price_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.price_tree = ttk.Treeview(price_frame, columns=('price', 'buy_value', 'sell_value', 'net_value'), show='headings')
        self.price_tree.heading('price', text='Giá')
        self.price_tree.heading('buy_value', text='Giá trị Buy')
        self.price_tree.heading('sell_value', text='Giá trị Sell')
        self.price_tree.heading('net_value', text='Giá trị Ròng')
        self.price_tree.column('price', anchor='e', width=100)
        self.price_tree.column('buy_value', anchor='e', width=150)
        self.price_tree.column('sell_value', anchor='e', width=150)
        self.price_tree.column('net_value', anchor='e', width=150)
        self.price_tree.grid(row=0, column=0, sticky="nsew")

        # Frame thông tin giá mới nhất
        latest_frame = ttk.LabelFrame(self.root, text="Thông tin giá mới nhất", padding=10)
        latest_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.latest_price_label = tk.Label(latest_frame, text="Giá mới nhất: N/A", anchor='w')
        self.latest_price_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.latest_volume_label = tk.Label(latest_frame, text="Khối lượng: N/A", anchor='w')
        self.latest_volume_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.match_type_label = tk.Label(latest_frame, text="Loại khớp: N/A", anchor='w')
        self.match_type_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Frame thống kê lệnh
        stats_frame = ttk.LabelFrame(self.root, text="Thống kê lệnh", padding=10)
        stats_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.num_buy_label = tk.Label(stats_frame, text="Số lệnh Buy: 0", anchor='w')
        self.num_buy_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_sell_label = tk.Label(stats_frame, text="Số lệnh Sell: 0", anchor='w')
        self.num_sell_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.avg_buy_volume_label = tk.Label(stats_frame, text="TB KL Buy: 0", anchor='w')
        self.avg_buy_volume_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.avg_sell_volume_label = tk.Label(stats_frame, text="TB KL Sell: 0", anchor='w')
        self.avg_sell_volume_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.total_buy_label = tk.Label(stats_frame, text="Tổng tiền Buy: 0", anchor='w')
        self.total_buy_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.total_sell_label = tk.Label(stats_frame, text="Tổng tiền Sell: 0", anchor='w')
        self.total_sell_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.net_money_label = tk.Label(stats_frame, text="Tiền ròng: 0", anchor='w')
        self.net_money_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Frame so sánh giá
        price_compare_frame = ttk.LabelFrame(self.root, text="So sánh giá", padding=10)
        price_compare_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.current_price_label = tk.Label(price_compare_frame, text="Giá hiện tại: N/A", anchor='w')
        self.current_price_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.sma5_price_label = tk.Label(price_compare_frame, text="Giá TB 5 ngày: N/A", anchor='w')
        self.sma5_price_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.sma10_price_label = tk.Label(price_compare_frame, text="Giá TB 10 ngày: N/A", anchor='w')
        self.sma10_price_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.sma20_price_label = tk.Label(price_compare_frame, text="Giá TB 20 ngày: N/A", anchor='w')
        self.sma20_price_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)

        # Frame so sánh khối lượng
        volume_compare_frame = ttk.LabelFrame(self.root, text="So sánh khối lượng", padding=10)
        volume_compare_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.today_volume_label = tk.Label(volume_compare_frame, text="KL hôm nay: N/A", anchor='w')
        self.today_volume_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.sma5_volume_label = tk.Label(volume_compare_frame, text="KL TB 5 ngày: N/A", anchor='w')
        self.sma5_volume_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.sma10_volume_label = tk.Label(volume_compare_frame, text="KL TB 10 ngày: N/A", anchor='w')
        self.sma10_volume_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.sma20_volume_label = tk.Label(volume_compare_frame, text="KL TB 20 ngày: N/A", anchor='w')
        self.sma20_volume_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)

        self.root.geometry("1200x800")

    def toggle_monitoring(self):
        if not self.running:
            self.running = True
            self.start_button.config(text="Dừng", bg="red")
            # Lấy giá trị symbol và interval trong luồng chính
            symbol = self.symbol.get()
            interval = self.interval.get()
            # Truyền symbol và interval vào luồng phụ
            self.monitor_thread = threading.Thread(target=self.monitor_stock, args=(symbol, interval), daemon=True)
            self.monitor_thread.start()
        else:
            self.running = False
            self.start_button.config(text="Bắt đầu", bg="green")
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join(timeout=1.0)

    def monitor_stock(self, symbol, interval):
        while self.running:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            intraday_data = stock.quote.intraday(symbol=symbol, page_size=10000, show_log=False)

            if intraday_data.empty:
                print(f"Không có dữ liệu cho mã {symbol} với khoảng thời gian {interval}")
                break
            if not self.running:
                break

            intraday_data['time'] = pd.to_datetime(intraday_data['time'])
            intraday_data = intraday_data.sort_values('time')
            intraday_data['net_value'] = intraday_data.apply(
                lambda row: row['price'] * row['volume'] if row['match_type'] == 'Buy' else - (row['price'] * row['volume']),
                axis=1
            )
            intraday_data['cumulative_net'] = intraday_data['net_value'].cumsum()

            self.intraday_data = intraday_data

            # Lên lịch cập nhật giao diện trong luồng chính
            self.root.after(0, self.display_info, intraday_data)
            self.root.after(0, self.display_price_stats, intraday_data)
            history_data = stock.quote.history(
                start=(pd.Timestamp.now() - pd.Timedelta(days=50)).strftime('%Y-%m-%d'),
                end=pd.Timestamp.now().strftime('%Y-%m-%d'),
                interval='1D'
            )
            self.root.after(0, self.display_comparison, intraday_data, history_data)

            # Xử lý khoảng thời gian chờ
            if interval.endswith('s'):
                sleep_time = int(interval[:-1])
            elif interval.endswith('p'):
                sleep_time = int(interval[:-1]) * 60
            else:
                sleep_time = 60
            time.sleep(sleep_time)

    def display_info(self, data):
        if data.empty:
            print("Không có dữ liệu intraday.")
            return
        latest = data.iloc[-1]
        self.latest_price_label.config(text=f"Giá mới nhất: {latest['price']:.2f}")
        self.latest_volume_label.config(text=f"Khối lượng: {latest['volume']:,}")
        self.match_type_label.config(text=f"Loại khớp: {latest['match_type']}")
        buy_orders = data[data['match_type'] == 'Buy']
        sell_orders = data[data['match_type'] == 'Sell']
        num_buy = len(buy_orders)
        num_sell = len(sell_orders)
        avg_buy_volume = buy_orders['volume'].mean() if num_buy > 0 else 0
        avg_sell_volume = sell_orders['volume'].mean() if num_sell > 0 else 0
        total_buy = (buy_orders['price'] * buy_orders['volume']).sum()
        total_sell = (sell_orders['price'] * sell_orders['volume']).sum()
        net_money = total_buy - total_sell
        self.num_buy_label.config(text=f"Số lệnh Buy: {num_buy:,}")
        self.num_sell_label.config(text=f"Số lệnh Sell: {num_sell:,}")
        self.avg_buy_volume_label.config(text=f"TB KL Buy: {avg_buy_volume:,.2f}")
        self.avg_sell_volume_label.config(text=f"TB KL Sell: {avg_sell_volume:,.2f}")
        self.total_buy_label.config(text=f"Tổng tiền Buy: {total_buy:,.0f}")
        self.total_sell_label.config(text=f"Tổng tiền Sell: {total_sell:,.0f}")
        self.net_money_label.config(text=f"Tiền ròng: {net_money:,.0f}")

    def display_price_stats(self, data):
        if data.empty:
            return
        data['value'] = data['price'] * data['volume']
        grouped = data.groupby(['price', 'match_type'])['value'].sum().unstack(fill_value=0)
        grouped['net_value'] = grouped.get('Buy', 0) - grouped.get('Sell', 0)
        for item in self.price_tree.get_children():
            self.price_tree.delete(item)
        for price, row in grouped.iterrows():
            self.price_tree.insert('', 'end', values=(f"{price:,.2f}", f"{row.get('Buy', 0):,.0f}", f"{row.get('Sell', 0):,.0f}", f"{row['net_value']:,.0f}"))

    def display_comparison(self, intraday_data, history_data):
        if history_data.empty:
            print("Không có dữ liệu lịch sử.")
            return
        closes = history_data['close'].values.astype(float)
        volumes = history_data['volume'].values.astype(float)
        sma5 = calculate_sma(closes, 5)
        sma10 = calculate_sma(closes, 10)
        sma20 = calculate_sma(closes, 20)
        vol_sma5 = calculate_sma(volumes, 5)
        vol_sma10 = calculate_sma(volumes, 10)
        vol_sma20 = calculate_sma(volumes, 20)
        current_price = closes[-1] if len(closes) > 0 else None
        today_volume = intraday_data['volume'].sum() if not intraday_data.empty else None
        self.current_price_label.config(text=f"Giá hiện tại: {current_price if current_price is not None else 'N/A':,.2f}")
        self.sma5_price_label.config(text=f"Giá TB 5 ngày: {sma5 if sma5 is not None else 'N/A':,.2f}")
        self.sma10_price_label.config(text=f"Giá TB 10 ngày: {sma10 if sma10 is not None else 'N/A':,.2f}")
        self.sma20_price_label.config(text=f"Giá TB 20 ngày: {sma20 if sma20 is not None else 'N/A':,.2f}")
        self.today_volume_label.config(text=f"KL hôm nay: {today_volume if today_volume is not None else 'N/A':,}")
        self.sma5_volume_label.config(text=f"KL TB 5 ngày: {vol_sma5 if vol_sma5 is not None else 'N/A':,.2f}")
        self.sma10_volume_label.config(text=f"KL TB 10 ngày: {vol_sma10 if vol_sma10 is not None else 'N/A':,.2f}")
        self.sma20_volume_label.config(text=f"KL TB 20 ngày: {vol_sma20 if vol_sma20 is not None else 'N/A':,.2f}")

def calculate_sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
