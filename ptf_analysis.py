# -*- coding: utf-8 -*-
"""Ptf_analysis

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OHnpj4nwmbdmKM1iwjh8393kWnBubG3I
"""

#!pip install fpdf
#!pip install yfinance
#!pip install reportlab

import yfinance as yf
import datetime
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import math
from scipy.stats import norm
import matplotlib.pyplot as plt
from math import *
from fpdf import FPDF
import os
from io import BytesIO
import matplotlib.dates as mdates
from scipy.stats import norm
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import tkinter as tk
from tkinter import filedialog


class Portfolio:
    trading_days_per_year = 252
    trading_days_per_week = 5
    trading_days_per_month = 20

    def __init__(self, assets: dict, start="2020-01-01", end=datetime.datetime.now().strftime("%Y-%m-%d")):
        self.assets = assets
        self.start = start
        self.end = end
        self.prices = self._download_prices()

    def _download_prices(self):
        p=yf.download(self.get_list_assets(), start=self.start, end=self.end)
        prices = yf.download(self.get_list_assets(), start=self.start, end=self.end)['Adj Close']

        p.to_excel('Prices.xlsx')
        return prices.dropna()

    def get_prices(self):
        return self.prices

    def get_list_assets(self):
        return  list(self.assets.keys())

    def get_list_qte(self):
        return list(self.assets.values())

   
    def calculate_assets_returns (self, periode = 1):
        return self.get_prices().pct_change(periods=periode).dropna()

    def get_trading_days(self):
        return len(self.calculate_assets_returns())



#Calculate the ptf value at each traiding day
    def get_ptf_value(self):
        ptf_value=round((self.get_prices() @ self.get_list_qte()).dropna(),3)
        test = (ptf_value -  self.get_ptf_value1()).sum()
        if test !=0:
            print ("rewiew the ptf_value instance")
            pass
        return ptf_value 

    def get_ptf_value1(self):
        return round(self.get_valo_each_asset().sum(axis=1).dropna(),3)


#calculate the value of each asset at each traiding day
    def get_valo_each_asset(self):
        return self.get_prices().mul(self.get_list_qte()).dropna()

#calculate the weights at each traiding day = asumption that the qté dosn't rebalanced each day
    def get_weights(self):
        return self.get_valo_each_asset().div(self.get_ptf_value(), axis=0).dropna()
    
#control of day weigts
    def control_weights(self):
        return self.get_weights().sum(axis=1)

    def calculate_weights_returns (self):
        return self.calculate_assets_returns().mul(self.get_weights()).dropna()

    def calculate_cov_matrix(self):
        return self.calculate_assets_returns().cov().dropna()

    def calculate_ptf_returns (self):
        return round(self.calculate_weights_returns().sum(axis=1).dropna(),3)

    def calculate_portfolio_volatility(self):
        return round(self.calculate_ptf_returns().std(),3)*sqrt(self.trading_days_per_year)


    def get_base_100_ptf(self):
        ptf_value = self.get_ptf_value()
        base_value = ptf_value.iloc[0]
        base_100_ptf= ptf_value / base_value * 100
        return round(base_100_ptf.dropna(),3)

#####################################################PERFORMANCE#########################@
########PERFORMANCE##################PERFORMANCE######PERFORMANCE################@
#########PERFORMANCE################PERFORMANCE#####PERFORMANCE###################@
####PERFORMANCE###############PERFORMANCE##########################################@
####################PERFORMANCE###############PERFORMANCE########PERFORMANCE########@
#Tcheked#############################################################@#@@@@@@@@

    def performance_ytd(self):
        base_100_ptf = self.get_base_100_ptf()
        start_datetime = datetime.datetime.strptime(self.start, "%Y-%m-%d")
        start_year = datetime.datetime(start_datetime.year, 1, 1).strftime("%Y-%m-%d")
        start_year_index = base_100_ptf.index.get_loc(start_year, method='nearest')
        return (base_100_ptf.iloc[-1] - base_100_ptf.iloc[start_year_index]) / 100

    def performance_1_week(self):
        base_100_ptf = self.get_base_100_ptf()
        return (base_100_ptf.iloc[-1] - base_100_ptf.iloc[-1 - self.trading_days_per_week])/100

    def performance_1_month(self):
        base_100_ptf = self.get_base_100_ptf()
        return (base_100_ptf.iloc[-1] - base_100_ptf.iloc[-1 - self.trading_days_per_month])/100

    def performance_1_year(self):
        base_100_ptf = self.get_base_100_ptf()
        if len(base_100_ptf) > self.trading_days_per_year:
            return (base_100_ptf.iloc[-1] - base_100_ptf.iloc[-1 - self.trading_days_per_year])/100
        else:
            print("Les données ne couvrent pas une année complète.")
            return None
       
#####################################################PERFORMANCE#########################@
########PERFORMANCE##################PERFORMANCE######PERFORMANCE################@
#########PERFORMANCE################PERFORMANCE#####PERFORMANCE###################@
####PERFORMANCE###############PERFORMANCE##########################################@
####################PERFORMANCE###############PERFORMANCE########PERFORMANCE########@
#Tcheked#############################################################@#@@@@@@@@
##PERFORMANCE#########PERFORMANCE########################PERFORMANCE#####################

#######BENCHMARK###########BENCHMARK##########BENCHMARK############BENCHMARKBENCHMARK
#######BENCHMARK############BENCHMARK##########BENCHMARK#####BENCHMARK#########&&&&&&&&&
#######BENCHMARK###########BENCHMARK##########BENCHMARK############BENCHMARKBENCHMARK
#######BENCHMARK############BENCHMARK##########BENCHMARK#####BENCHMARK#########&&&&&&&&&
    def download_bench(self,bench='^FCHI'):
            return yf.download(bench, start=self.start, end=self.end)['Adj Close'].dropna()

    def bench_returns(self,bench='^FCHI'):
        return self.download_bench().pct_change().dropna()

    def get_base_100_benchmark(self, bench='^FCHI'):
        benchmark_prices = self.download_bench(bench)
        base_value = benchmark_prices.iloc[0]
        base_100_benchmark = benchmark_prices / base_value * 100
        return base_100_benchmark.dropna()
#######BENCHMARK###########BENCHMARK##########BENCHMARK############BENCHMARKBENCHMARK
#######BENCHMARK############BENCHMARK##########BENCHMARK#####BENCHMARK#########&&&&&&&&&
#######BENCHMARK###########BENCHMARK##########BENCHMARK############BENCHMARKBENCHMARK
#######BENCHMARK############BENCHMARK##########BENCHMARK#####BENCHMARK#########&&&&&&&&&
    def information_ratio(self, bench='^FCHI'):
        returns = self.calculate_ptf_returns().fillna(0)
        bench_returns = self.bench_returns(bench).fillna(0)
        diff_rets = returns - bench_returns
        information_ratio= diff_rets.mean() / diff_rets.std()
        return round(information_ratio,3)


    def greeks(self, bench='^FCHI'):
        returns = self.calculate_ptf_returns()
        bench_returns = self.bench_returns(bench)

        # find covariance
        matrix = np.cov(returns, bench_returns)
        beta = matrix[0, 1] / matrix[1, 1]

        # calculates measures 
        alpha = returns.mean() - beta * bench_returns.mean()
        alpha = alpha * self.trading_days_per_year
        return round(alpha,3), round(beta,3)


    def historical_var(self, confidence_level=0.95):
        ptf_returns = self.calculate_ptf_returns()
        var = -np.percentile(ptf_returns, (1 - confidence_level) * 100)
        return round(var,3)


    def parametric_var(self, confidence_level=0.95):
        ptf_returns = self.calculate_ptf_returns()
        mean_returns = ptf_returns.mean()
        std_returns = ptf_returns.std()

        var = (mean_returns - std_returns * norm.ppf(1 - confidence_level))
        return round(var,3)

    def monte_carlo_var(self, confidence_level=0.95, num_simulations=10000):
        ptf_returns = self.calculate_ptf_returns()
        mean_returns = ptf_returns.mean()
        std_returns = ptf_returns.std()

        simulated_returns = np.random.normal(loc=mean_returns, scale=std_returns, size=num_simulations)
        var = -np.percentile(simulated_returns, (1 - confidence_level) * 100)
        return round(var,3)

    def print_var(self, confidence_level=0.95, num_simulations=10000):
        print(f"Historical VaR (confidence level: {confidence_level}): {self.historical_var(confidence_level)}")
        print(f"Parametric VaR (confidence level: {confidence_level}): {self.parametric_var(confidence_level)}")
        print(f"Monte Carlo VaR (confidence level: {confidence_level}, simulations: {num_simulations}): {self.monte_carlo_var(confidence_level, num_simulations)}")

    def print_summary(self, confidence_level=0.95, num_simulations=10000):
        print("\nSummary of Portfolio:")
        print("\nNumber of trading days:", self.get_trading_days())
        print("\nPortfolio value:")
        print(self.get_ptf_value().tail())
        print("\nPortfolio returns:")
        print(self.calculate_ptf_returns().tail())
        print("\nPortfolio volatility:", self.calculate_portfolio_volatility())
        print("\nInformation ratio:", self.information_ratio())
        print("\nAlpha and Beta (Greeks):", self.greeks())
        self.print_var(confidence_level, num_simulations)

    def get_non_zero_weights(self):
        weights = self.get_weights()
        non_zero_weights = weights.loc[:, (weights != 0).any(axis=0)]
        return non_zero_weights

    def plot_portfolio_info2(self):
        sns.set(style="whitegrid")
        plt.style.use('seaborn-darkgrid')
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))

        # Plot Portfolio Value
        self.get_ptf_value().plot(ax=axes[0, 0], title="Portfolio Value", lw=2, color='royalblue')
        axes[0, 0].set_ylabel("Value")
        
        # Plot Portfolio Returns
        portfolio_returns = self.calculate_ptf_returns()
        portfolio_returns.plot(ax=axes[0, 1], title="Portfolio Returns", lw=2, color='darkorange')
        axes[0, 1].set_ylabel("Returns")

        # Plot VaR lines on Portfolio Returns
        historical_var = self.historical_var()
        parametric_var = self.parametric_var()
        monte_carlo_var = self.monte_carlo_var()

        axes[0, 1].axhline(y=-historical_var, color='r', linestyle='--', label=f'Historical VaR ({-historical_var:.2%})')
        axes[0, 1].axhline(y=-parametric_var, color='g', linestyle='--', label=f'Parametric VaR ({-parametric_var:.2%})')
        axes[0, 1].axhline(y=-monte_carlo_var, color='b', linestyle='--', label=f'Monte Carlo VaR ({-monte_carlo_var:.2%})')

        axes[0, 1].legend()

        # Plot Portfolio vs. Benchmark
        ptf_base_100 = self.get_base_100_ptf()
        bench_base_100 = self.get_base_100_benchmark()
        data = pd.concat([ptf_base_100, bench_base_100], axis=1)
        data.columns = ['Portfolio', 'Benchmark']
        data.plot(ax=axes[1, 0], title="Portfolio vs. Benchmark", lw=2)
        axes[1, 0].set_ylabel("Base 100")

        
        axes[1, 1].axis("off")
        summary_text = f"Volatility: {round(self.calculate_portfolio_volatility(),3)}\n"
        summary_text += f"Alpha: {self.greeks()[0]}\n"
        summary_text += f"Beta: {self.greeks()[1]}\n"
        summary_text += f"Perf YTD: {round(self.performance_ytd(),3)}\n"
        summary_text += f"Perf 1 an: {round(self.performance_1_year(),3)}\n"
        summary_text += f"Perf 1 week: {round(self.performance_1_week(),3)}\n"
        summary_text += f"Perf 1 month: {round(self.performance_1_month(),3)}\n"
        axes[1, 1].text(0.5, 0.5, summary_text, horizontalalignment='center', verticalalignment='center', fontsize=12, transform=axes[1, 1].transAxes)

        # Improve plot spacing
        plt.tight_layout()

        fig.savefig("Ptf_analysis.png")

        # Show the plot
        plt.show()
        return fig

    def export_to_pdf(self, filename="Portfolio_Analysis.pdf"):
        fig = self.plot_portfolio_info2()
        plot_filename = "Ptf_analysis_temp.png"
        fig.savefig(plot_filename)

        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # Add title
        styles = getSampleStyleSheet()
        title = "Portfolio Analysis"
        story.append(Paragraph(title, styles['Title']))

        # Add introduction
        intro_text = "This report provides a comprehensive analysis of our current investment portfolio. It highlights the performance, asset allocation, and risk metrics to help guide future decision-making and optimize returns."
        story.append(Paragraph(intro_text, styles['Normal']))

        # Add plot image
        story.append(Spacer(1, 12))
        img = Image(plot_filename, width=500, height=400)
        story.append(img)

        # Build the PDF
        doc.build(story)
        print(f"Portfolio analysis exported to {filename}")

        # Remove the temporary plot file
        os.remove(plot_filename)

#création du ptf
#df = pd.read_excel ('PTF.xlsx')
#new_df = df[["Tickers", "Qté"]]
#list_tickers = new_df["Tickers"].to_list()
#list_qte = new_df["Qté"].to_list()
#ptf = {}
#for i in range(len(list_tickers)):
    #ptf[list_tickers[i]] = list_qte[i]


#instanciation
#Ptf= Portfolio({'CAC':1},start='2000-12-01')
#Ptf._download_prices()

import tkinter as tk
from tkinter import filedialog


class PortfolioApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Portfolio Analysis")

        self.file_label = tk.Label(self.window, text="Excel File:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_entry = tk.Entry(self.window)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)

        self.browse_button = tk.Button(self.window, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.start_date_label = tk.Label(self.window, text="Start Date (YYYY-MM-DD):")
        self.start_date_label.grid(row=1, column=0, padx=5, pady=5)

        self.start_date_entry = tk.Entry(self.window)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.end_date_label = tk.Label(self.window, text="End Date (YYYY-MM-DD):")
        self.end_date_label.grid(row=2, column=0, padx=5, pady=5)

        self.end_date_entry = tk.Entry(self.window)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=5)

        self.analyze_button = tk.Button(self.window, text="Analyze Portfolio", command=self.analyze_portfolio)
        self.analyze_button.grid(row=3, columnspan=3, padx=5, pady=5)

        self.export_button = tk.Button(self.window, text="Export to PDF", command=self.export_to_pdf)
        self.export_button.grid(row=4, columnspan=3, padx=5, pady=5)

        self.window.mainloop()


    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def analyze_portfolio(self):
        file_path = self.file_entry.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        df = pd.read_excel(file_path)
        new_df = df[["Tickers", "Qté"]]
        list_tickers = new_df["Tickers"].to_list()
        list_qte = new_df["Qté"].to_list()
        ptf = {}
        for i in range(len(list_tickers)):
            ptf[list_tickers[i]] = list_qte[i]

        portfolio = Portfolio(ptf, start=start_date, end=end_date)
        portfolio.print_summary()
        return portfolio
        #portfolio.export_to_pdf()

    def export_to_pdf(self):
        #file_path = self.file_entry.get()
    #    start_date = self.start_date_entry.get()
#        end_date = self.end_date_entry.get()

 #       df = pd.read_excel(file_path)
  #      new_df = df[["Tickers", "Qté"]]
   #     list_tickers = new_df["Tickers"].to_list()
    #    list_qte = new_df["Qté"].to_list()
   #     ptf = {}
     ##   for i in range(len(list_tickers)):
    #        ptf[list_tickers[i]] = list_qte[i]

        portfolio = self.analyze_portfolio()
        portfolio.export_to_pdf("Portfolio_Analysis1.pdf")

if __name__ == "__main__":
    app = PortfolioApp()
