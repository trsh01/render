(async () => {
  const options = {
		method: "POST", 
		headers: { 
			Accept: "application/json"
			},
		body: JSON.stringify({
			params: {
    				symbol: 'BTCUSDT', 
    				interval: '1h', 
    				limit: 5
				}
			})
		}

  const data = await fetch(
    'https://api.binance.com/api/v3/klines',options
  ).then(response => response.json());

  // create the chart
  Highcharts.stockChart('container', {
    rangeSelector: {
      selected: 1
    },

    title: {
      text: 'AAPL Stock Price'
    },

    series: [
      {
        type: 'candlestick',
        name: 'AAPL Stock Price',
        data: data,
        dataGrouping: {
          units: [
            [
              'week', // unit name
              [1] // allowed multiples
            ],
            ['month', [1, 2, 3, 4, 6]]
          ]
        }
      }
    ]
  });
})().catch(console.error);
