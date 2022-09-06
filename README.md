# OptionsChainVisualizer

This is a simple python script meant to visualize the options chain for any security across all expirations in order to find potential ["Gamma Ramps"](https://www.investopedia.com/terms/g/gamma-hedging.asp)

Note: You will need a subscription to the "Starter" options data package from polygon.io in order to get updated options data. This repo contains a pickle file cache of historial BBBY and GME options data for testing and demonstration purposes. If you would like to demo the code without subscribing to polygon.io simple set 'USECACHE' to be True.

The following settings are available to change within the source code:
<img width="875" alt="image" src="https://user-images.githubusercontent.com/40746816/188523254-2e57fa78-1823-4b17-aef0-6a38c5d8198f.png">

Cumulative Example (BBBY):
![BBBY cumulative options data](https://user-images.githubusercontent.com/40746816/188523279-37467d21-b12a-4e50-8fc0-3193d5012c8c.png)


Non-Cumulative Example (BBBY):
![BBBY non-cumulative options](https://user-images.githubusercontent.com/40746816/188523284-43cbb5bb-e27e-4fac-9e63-f6fa07b41f19.png)

