from flask import Flask, render_template, request, jsonify
import requests
import datetime

app = Flask(__name__)

# Lista para armazenar as transações e o portfólio
transactions = []
portfolio = {}

# Função para buscar o preço atual de uma ação usando a API Brapi
def get_stock_price(symbol):
    url = f'https://brapi.dev/api/quote/{symbol}?token=7c6tLDYzAqbUp8k3MBhCzx' 
    response = requests.get(url)
    data = response.json()

    if 'results' in data and data['results']:
        result = data['results'][0]
        price = result['regularMarketPrice']
        date = result['regularMarketTime']
        return price, date
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
        avg_buy_price = portfolio[symbol]['avg_buy_price']
        total_cost = portfolio[symbol]['total_cost']
        profit_loss = (sell_price - avg_buy_price) * quantity
        
        portfolio[symbol]['quantity'] -= quantity
        portfolio[symbol]['total_cost'] -= avg_buy_price * quantity
        
        if portfolio[symbol]['quantity'] == 0:
            del portfolio[symbol]

        transaction = {
            'symbol': symbol,
            'quantity': quantity,
            'price': sell_price,
            'type': 'sell',
            'date': datetime.datetime.now().isoformat(),
            'profit_loss': profit_loss
        }
        
        transactions.append(transaction)
        
        return jsonify({'message': f'Venda simulada realizada com sucesso. Lucro/Prejuízo: R${profit_loss:.2f}', 'portfolio': portfolio})
    else:
        return jsonify({'error': 'Você não tem ações suficientes para vender'}), 400

# Rota para obter o histórico de transações
@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

# Rota para obter o portfólio
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(portfolio)

# Função para buscar o histórico de preços de uma ação usando a API Brapi
def get_stock_history(symbol):
    url = f'https://brapi.dev/api/quote/{symbol}?range=1mo&interval=1d&token=7c6tLDYzAqbUp8k3MBhCzx'
    response = requests.get(url)
    data = response.json()

    if 'results' in data and data['results']:
        result = data['results'][0]
        if 'historicalDataPrice' in result:
            history = result['historicalDataPrice']
            return history
    return None


# Rota para obter o histórico de uma ação
@app.route('/get_stock_history', methods=['POST'])
def get_stock_history_route():
    symbol = request.form.get('symbol')
    history = get_stock_history(symbol)
    
    if history:
        dates = [item['date'] for item in history]
        prices = [item['close'] for item in history]
        return jsonify({'dates': dates, 'prices': prices})
    else:
        return jsonify({'error': 'Erro ao buscar histórico da ação'}), 400

if __name__ == '__main__':
    app.run(debug=True)
