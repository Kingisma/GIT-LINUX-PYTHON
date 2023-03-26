#!/bin/bash

# Get the Bitcoin price
PRICE=$(curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin" | grep -Eo '"current_price":[0-9]+(\.[0-9]+)?' | cut -d ':' -f 2)

# Print the price to the console
echo  "\$$PRICE"

