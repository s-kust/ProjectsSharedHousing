import os, shutil
from pathlib import Path
import pandas as pd
import numpy as np
from django.core.management import BaseCommand
from django.core.management import call_command 
from django.conf import settings
from portfoliopositionsreport.models import Portfolio, PortfolioRow
import portfoliopositionsreport.portfolio_report_images_not_delete as portfolio_report


class Command(BaseCommand):
    help = "Update portfolio using portfolio_report_images_not_delete script"

    def handle(self, *args, **options):
        self.stdout.write()
        self.stdout.write("update_portfolio start 4")

        data_store = portfolio_report.process_full()
        portfolio_rows = data_store.all_ideas
        # portfolio_rows = portfolio_report.create_portfolio_df_from_worksheets()
        # base_path = '/media/'
        base_path = ''
        assert isinstance(portfolio_rows, pd.DataFrame)
        portfolio_today = Portfolio.objects.create()
        for _, row in portfolio_rows.iterrows():
            assert row['Type'] in ["Stocks_ETFs", "Forex"]
            assert not pd.isna(row['Ticker1'])
            portfolio_row = PortfolioRow.objects.create(
                portfolio=portfolio_today, ticker_1=row['Ticker1'], \
                row_type=row['Type'], note=row['Note'])
            portfolio_row.ticker_2 = np.where(pd.isna(row['Ticker2']), "", row['Ticker2'])
            if not pd.isna(row['Ticker2']) and row['Type'] == "Stocks_ETFs":
                filename_1 = row['Ticker1'] + "_" + row['Ticker2'] + ".png"
                filename_1 = os.path.join(base_path, filename_1)
                portfolio_row.file_1 = filename_1               
            else:
                if row['Type'] == "Forex":
                    filename_1 = row['Ticker1'] + "-" + row['Ticker2'] + "_short_period" + ".png"                    
                    filename_2 = row['Ticker1'] + "-" + row['Ticker2'] + "_long_period" + ".png"
                    filename_1 = os.path.join(base_path, filename_1)
                    filename_2 = os.path.join(base_path, filename_2)
                    portfolio_row.file_1 = filename_1
                    portfolio_row.file_2 = filename_2
                else:
                    filename_1 = row['Ticker1'] + "_short_period" + ".png"
                    filename_2 = row['Ticker1'] + "_long_period" + ".png"
                    filename_1 = os.path.join(base_path, filename_1)
                    filename_2 = os.path.join(base_path, filename_2)
                    portfolio_row.file_1 = filename_1
                    portfolio_row.file_2 = filename_2
            portfolio_row.save()            
        rows_all = PortfolioRow.objects.all()
        print('rows_all', len(rows_all))
        rows_set = portfolio_today.portfoliorow_set.all()
        print('rows_set', len(rows_set))
        for portfolio_row in rows_set:
            print(portfolio_row)
        date_last_update = Portfolio.objects.all()[0].last_update_date
        # print('date_last_update', date_last_update)
        print('date_last_update', date_last_update.strftime("%d-%B-%Y"))
        folder = './staticfiles/'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        call_command('collectstatic')
        self.stdout.write("update_portfolio end")
        self.stdout.write()
