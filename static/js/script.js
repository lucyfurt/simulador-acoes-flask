let portfolio = {}; // Armazena o portfólio do usuário

        async function getStockPrice() {
            const symbol = document.getElementById("symbol").value;
            const response = await fetch("/get_stock", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `symbol=${symbol}`,
            });
            const data = await response.json();
            console.log("Dados do preço da ação:", data);
            if (data.price) {
                document.getElementById("price").innerText = `Preço Atual: $${data.price}`;
                document.getElementById("buy-section").style.display = "block";
                document.getElementById("sell-section").style.display = "block";
                document.getElementById("current-price").value = data.price; // Atualiza o preço atual
                loadStockHistory(symbol); // Carrega o histórico de preços ao buscar o preço atual
            } else {
                alert("Erro ao buscar preço da ação");
            }
        }

        async function loadStockHistory(symbol) {
    const response = await fetch("/get_stock_history", {
        method: "POST", // Altere para POST
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `symbol=${symbol}`, // Enviar o símbolo da ação no corpo
    });

    const data = await response.json();
    console.log("Histórico de preços:", data);

    const historyDiv = document.getElementById("stock-history");
    historyDiv.innerHTML = `<h3>Histórico de Preços para ${symbol}</h3>`;
    if (data.dates.length === 0) {
        historyDiv.innerHTML += "<p>Nenhum histórico disponível.</p>";
        return;
    }

    const historyTable = document.createElement("table");
    const header = `
        <thead>
            <tr>
                <th>Data</th>
                <th>Preço ($)</th>
            </tr>
        </thead>
        <tbody>
    `;
    historyTable.innerHTML = header;

    data.dates.forEach((date, index) => {
        const row = `
            <tr>
                <td>${new Date(date).toLocaleDateString()}</td>
                <td>$${data.prices[index].toFixed(2)}</td>
            </tr>
        `;
        historyTable.innerHTML += row;
    });

    historyTable.innerHTML += `</tbody>`;
    historyDiv.appendChild(historyTable);
}


        async function buyStock() {
            const symbol = document.getElementById("symbol").value;
            const quantity = document.getElementById("quantity").value;
            const price = document.getElementById("current-price").value;

            if (!symbol || !quantity || !price) {
                console.error("Por favor, preencha todos os campos.");
                return; // Sai da função se algum campo não estiver preenchido
            }

            console.log(`Comprando ${quantity} ações de ${symbol} a $${price}`);
            const response = await fetch("/buy_stock", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `symbol=${symbol}&quantity=${quantity}&price=${price}`,
            });
            const data = await response.json();
            console.log("Resposta da compra:", data);
            alert(data.message);
            updatePortfolio(); // Atualiza o portfólio após a compra
            loadTransactions(); // Recarregar transações após a compra
        }

        async function sellStock() {
            const symbol = document.getElementById("symbol").value;
            const quantity = document.getElementById("sell-quantity").value;
            const price = document.getElementById("current-price").value;

            const response = await fetch("/sell_stock", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `symbol=${symbol}&quantity=${quantity}&price=${price}`,
            });
            const data = await response.json();
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
                updatePortfolio(); // Atualiza o portfólio após a venda
                loadTransactions(); // Recarregar transações após a venda
            }
        }

        async function loadTransactions() {
            const response = await fetch("/transactions");
            const transactions = await response.json();

            const tableBody = document.getElementById("transactions-body");
            tableBody.innerHTML = ""; // Limpa a tabela antes de preenchê-la

            transactions.forEach((transaction) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${transaction.symbol}</td>
                    <td>${transaction.quantity}</td>
                    <td>${transaction.price}</td>
                    <td>${transaction.type}</td>
                    <td>${new Date(transaction.date).toLocaleString()}</td>
                `;
                tableBody.appendChild(row);
            });
        }

        async function updatePortfolio() {
            const response = await fetch("/portfolio");
            portfolio = await response.json();
            updatePortfolioDisplay();
        }

        async function updatePortfolioDisplay() {
            const portfolioDiv = document.getElementById('portfolio');
            portfolioDiv.innerHTML = '<h3>Seu Portfólio</h3>';
            const chartData = {
                labels: [],
                datasets: []
            };

            if (Object.keys(portfolio).length === 0) {
                portfolioDiv.innerHTML += '<p>Nenhuma ação comprada ainda.</p>';
            } else {
                const fetchPromises = []; // Para armazenar todas as promessas

                for (const symbol in portfolio) {
                    const stock = portfolio[symbol];
                    portfolioDiv.innerHTML += `
                        <p>${symbol}: ${stock.quantity} ações | Preço Médio: $${(stock.total_cost / stock.quantity).toFixed(2)}</p>
                    `;

                    // Gerar dados de desempenho para o gráfico
                    const promise = fetchStockHistory(symbol).then(history => {
                        chartData.labels = history.dates;
                        chartData.datasets.push({
                            label: symbol,
                            data: history.prices,
                            fill: false,
                            borderColor: getRandomColor(),
                            tension: 0.1
                        });
                    });

                    fetchPromises.push(promise);
                }

                // Aguarde todas as promessas serem resolvidas
                await Promise.all(fetchPromises);
                // Atualizar gráfico com os dados
                updateChart(chartData);
            }
        }

        async function fetchStockHistory(symbol) {
            const response = await fetch(`/get_stock_history?symbol=${symbol}`);
            const data = await response.json();
            console.log("Histórico de preços:", data);

            return {
                dates: data.dates,
                prices: data.prices
            };
        }

        function updateChart(chartData) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    // Destruir o gráfico existente se já houver um criado, para evitar erros
    if (window.performanceChart) {
        window.performanceChart.destroy();
    }

    // Criar o novo gráfico
    window.performanceChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    },
                    title: {
                        display: true,
                        text: 'Data'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Preço ($)'
                    }
                }
            }
        }
    });
}

        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        // Inicializa o portfólio e transações ao carregar a página
        window.onload = () => {
            updatePortfolio();
            loadTransactions();
        };
