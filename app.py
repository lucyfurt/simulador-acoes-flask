from flask import Flask, render_template, request, jsonify
import requests
import datetime

app = Flask(__name__)

# Chave da API Alpha Vantage
ALPHA_VANTAGE_API_KEY = 'W9FV8FI10UCWJ7QC'

# Lista para armazenar as transações e o portfólio
transactions = []
portfolio = {}

# Função para buscar o preço atual de uma ação
def get_stock_price(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()
    time_series = data.get('Time Series (5min)', {})
    
    if time_series:
        latest_time = list(time_series.keys())[0]
        latest_data = time_series[latest_time]
        return float(latest_data['4. close']), latest_time
    return None, None

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para buscar preço de ação
@app.route('/get_stock', methods=['POST'])
def get_stock():
    symbol = request.form.get('symbol')
    price, date = get_stock_price(symbol)
    
    if price:
        return jsonify({'symbol': symbol, 'price': price, 'date': date})
    else:
        return jsonify({'error': 'Erro ao buscar preço da ação'})

# Rota para simular compra de ação
@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    symbol = request.form.get('symbol')
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price'))
    
    # Atualizando o portfólio do usuário
    if symbol in portfolio:
        portfolio[symbol]['quantity'] += quantity
        portfolio[symbol]['total_cost'] += quantity * price
    else:
        portfolio[symbol] = {
            'quantity': quantity,
            'total_cost': quantity * price,
            'avg_buy_price': price
        }
    
    transaction = {
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'type': 'buy',
        'date': datetime.datetime.now().isoformat()
    }
    
    transactions.append(transaction)
    
    return jsonify({'message': 'Compra simulada realizada com sucesso', 'portfolio': portfolio})

# Rota para simular venda de ação
@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    symbol = request.form.get('symbol')
    quantity = int(request.form.get('quantity'))
    sell_price = float(request.form.get('price'))
    
    # Verificar se o usuário tem ações suficientes para vender
    if symbol in portfolio and portfolio[symbol]['quantity'] >= quantity:
        # Calculando lucro ou prejuízo
        avg_buy_price = portfolio[symbol]['avg_buy_price']
        total_cost = portfolio[symbol]['total_cost']
        profit_loss = (sell_price - avg_buy_price) * quantity
        
        # Atualizando o portfólio
        portfolio[symbol]['quantity'] -= quantity
        portfolio[symbol]['total_cost'] -= avg_buy_price * quantity
        
        # Remover a ação do portfólio se a quantidade for zero
        if portfolio[symbol]['quantity'] == 0:
            del portfolio[symbol]

        # Registrar a transação de venda
        transaction = {
            'symbol': symbol,
            'quantity': quantity,
            'price': sell_price,
            'type': 'sell',
            'date': datetime.datetime.now().isoformat(),
            'profit_loss': profit_loss
        }
        
        transactions.append(transaction)
        
        return jsonify({'message': f'Venda simulada realizada com sucesso. Lucro/Prejuízo: ${profit_loss:.2f}', 'portfolio': portfolio})
    else:
        return jsonify({'error': 'Você não tem ações suficientes para vender'}), 400

# Rota para obter o histórico de transações
@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)  # Retorna a lista de transações em formato JSON

# Rota para obter o portfólio
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(portfolio)  # Retorna o portfólio em formato JSON

if __name__ == '__main__':
    app.run(debug=True)
