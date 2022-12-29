# Data is current as of December 28, 2022

# import libraries
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import linalg as la

class Player:
    """
    Create a "player" object with the following attributes
        - Name (string)
        - Team (string)
        - Position (string)
        - Salary (float)
        - Points Per Game (float)
        - Rebounds Per Game (float)
        - Assist-to-Turnover Ratio Per Game (float)
        - Games played (int)
        - Value Score
    """
    def __init__(self, newList):
        # Other data will be added from other spreadsheets
        self.name = newList[0]
        self.team = newList[1]
        self.salary = newList[2]
        self.pos = newList[3]
        self.games = newList[4]
        self.rpg = newList[5]
        self.assist = newList[6]
        self.stl = newList[7]
        self.blk = newList[8]
        self.tov = newList[9]
        self.ppg = newList[10]
        self.val = -1 # Value will be calculated later

    def __str__(self):
        return self.name

    def setValue(self):
        """This function gets the overall value of a player, based on my calculations for a valuable player
        - Value will be calculated based on the ability to contribute, whether directly or indirectly.
        - A player can contribute through two ways: points and possessions
            - ppg and assist contribute to points
            - rpg , stl, blk, and tov's contribute to possessions (tov's in a negative way)
        - According to stats.inpredictable.com, the average points per possession of the league is 1.12 ppp
        - Assuming a block is a missed shot, the defensive rebound rate of the NBA is about 76%
        """
        PPP = 1.12
        DRR = 0.76
        score = 0
        score += self.ppg
        # Assume each assist yields 2 points on average. May alter this later
        score += self.assist * 2
        score += (self.rpg + self.stl + self.blk * DRR - self.tov) * PPP
        self.val = score
    
    def setRatio(self):
        self.ratio = self.salary / self.val
    




# We will organize the player stats by performing some data wrangling

def dataWrangle():
    """This function wrangles the data. It returns a dataframe"""
    contracts_table = pd.read_excel(r'player_contracts.xlsx')
    # Now we need to remove some columns
    keepLabels1 = ["Player", "Tm", "2022-23"]
    for label in contracts_table.columns:
        if label not in keepLabels1:
            del contracts_table[label]
    #print(contracts_table)

    stats_table = pd.read_excel(r'player_stats_pg.xlsx')
    # Now we need to delete some columns
    keepLabels2 = ["Player", "G", "TRB", "AST", "TOV", "PTS", "Pos", "STL", "BLK"]
    for label in stats_table.columns:
        if label not in keepLabels2:
            del stats_table[label]

    # Now that we have both tables, we need to merge the two
    data = pd.merge(contracts_table, stats_table, on="Player")
    data.rename(columns= {'2022-23':'Salary'}, inplace=True)
    # We need to remove players that don't have a listed salary
    data = data.dropna()
    # This only drops 5 players
    # Now let's drop players that have played less than 5 games
    data = data.loc[data["G"] > 5]
    # This drops 18 players
    return data

def main():
    data = dataWrangle()
    data_array = data.to_numpy()
    m,n = data_array.shape

    player_list = [None]*m
    for i in range(m):
        newList = [data_array[i,j] for j in range(n)]
        player_list[i] = (Player(newList))

    # Now we calculate the value for each player
    for player in player_list:
        player.setValue()
        player.setRatio()
    
    # Now let's do some graphing
    graph_values(player_list)
    #printMVP(player_list)
    #printOverpaid(player_list)

    #Bugs to fix: Why are there doubl-ups? It's only for some. Not for everyone



def graph_values(player_list):
    # I will create a line of best fit
    # A is an mx2 matrix
    # b is an mX1 matrix
    m = len(player_list)
    A = np.ones((m,2))
    b = np.zeros(m)
    i = 0
    for player in player_list:
        A[i,0] = player.salary
        b[i] = player.val
        plt.plot(A[i,0], b[i], 'b.')
        i += 1
    X = la.lstsq(A,b)
    slope, intercept = X[0]
    domain = np.linspace(0, np.max(A[:,0]), 500)
    plt.plot(domain, domain*slope + intercept, 'r-')
    plt.xlabel("Salary")
    plt.ylabel("Player Value")
    plt.title("Player Value vs. Salary")
    plt.show()


def printMVP(player_list):
    """This function prints players in order from most valuable to least valuable
    This does not account for a player's salary"""
    print("Most Valuable Players:\n")
    MVP = sorted(player_list, key=lambda player: player.val, reverse=True)
    for player in MVP:
        print(player,round(player.val, 2))

def printOverpaid(player_list):
    """This function prinits players in order from most overpaid to most 'cost-effective' (so to speak)"""
    overpaid = sorted(player_list, key=lambda player: player.ratio, reverse=True)
    print("Most Overpaid Players:\n")
    for player in overpaid:
        print(player,round(player.ratio,2))


    
    