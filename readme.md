# Meta Trader 5 python Autotrader Project

- This project will be convering the basics of technical analysis and plotting.
- Furthermore, this project will take a look into backtesting for different stratergies based upon publically released data like CPI.
- Future prospects include use of Sentiment analysis, Renforcement Learning, and LLM integration as overwatch

## State Variables

- Before thinking about making millions with trading, I need to clearly define what and how the trading process will occuring and based on what. To implement this we first define what "state variables" I will be using.

- In the basic implementation of a trader, I took a look at a NFA state based approach for patter recognition on the classified events. It has its drawbacks like defining every single patter or having complex multivalued events. One can even extend it to a markov chain approach to see what the probability could be if one single pattern is observed to morph into another pattern. However it lacks soul and dynamics.

- The next approach would be to build upon this basic approach with a more detailed state taking into consideration the pip movement. Three bullish candle sticks with a net pip movement of 10 vs one with 50 makes all the difference when it comes to technical analysis. 
  - Taking a look into different timezone based market sessions to find overlap for more effective trade
  - Taking into account the volume
  - Looking at pip movement within a pattern
  - Correlation with Indicies like CPI to enhance prediction
  - Looking at Indicators like KDJ(9,3,3)/RSI and setting up zones

- That being said, what is mentioned above is only for detecting if we wanna buy or sell, but fails to account for duration! For CFD trading, we can treat it as futures, hence having an unlimited time of expiry. This leads to some intresting situations with the possibility of infinite loss (with leverage) which can cause our account to hit zero. To mitigate this, it is good to set realistic take profits and stop losses. Therefore to execute a trade automatically these variables need to be defined.
  - Buy or Sell
  - lot size
  - TP/SL
  - Close Trade (0/1)
- There may be additional things we can set up as well to mitigate losses before TP or SL have been hit. However those are complex in nature and would require multi agent systems.

# Sources
- investing.com
- forexfactory.com