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