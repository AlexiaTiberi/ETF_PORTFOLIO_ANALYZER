import pandas as pd
from src.functions import parse_amundi_filename

class IShareETF:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = {}
        self.holdings = pd.DataFrame()
        self.history = pd.DataFrame()
        self._parse_file()

    def _parse_file(self):
        raw_df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name=0) # this page should be partecipation /holdings
        df = pd.read_excel(self.file_path, skiprows=7, engine="openpyxl", sheet_name=0) # this page should be partecipation /holdings
        self.metadata["fund_name"] = str(raw_df.iloc[0, 0])
        self.metadata["inception_date"] = str(raw_df.iloc[1, 1])
        self.metadata["num_securities"] = raw_df.iloc[3, 1]
        self.metadata["curr_value"] = float(pd.read_excel(self.file_path, engine="openpyxl", sheet_name=2).iloc[0, 2]) # this page should be NAV/history
        self.history = pd.read_excel(self.file_path, engine="openpyxl", sheet_name=2) # this page should be NAV/history
        df = self._clean_holdings_dataframe(df, source="ishare")
        self.holdings = df

    def _clean_holdings_dataframe(self, df, source):
        column_mapping = {
            "ishare": {
                "Ticker dell'emittente": "Ticker",
                "Nome": "Name",
                "Settore": "Sector",
                "Ponderazione (%)": "Weight",
                "Area Geografica": "Location",
                "Asset Class": "Asset_Class",
                "Valuta di mercato": "Currency"
            }
        }
        df = df.rename(columns=column_mapping[source])
        df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
        return df[['Ticker', 'Name', 'Sector', 'Asset_Class', 'Weight', 'Location', 'Currency']]

    def get_exposure_by(self, group_by: str) -> pd.DataFrame:
        """
        Returns the percentage weight exposure of the ETF grouped by the specified column.

        Parameters:
            group_by (str): The column name to group by (e.g., 'Location', 'Sector').

        Returns:
            pd.DataFrame: Sorted DataFrame with two columns: [group_by, 'Weight'].
        """
        if group_by not in self.holdings.columns or 'Weight' not in self.holdings.columns:
            return pd.DataFrame(columns=[group_by, 'Weight'])

        grouped = self.holdings.groupby(group_by)['Weight'].sum().reset_index()
        grouped = grouped.sort_values(by='Weight', ascending=False).reset_index(drop=True)
        return grouped

    def __repr__(self):
        return (
            f"IShareETF(\n"
            f"  file_path={self.file_path},\n"
            f"  fund_name={self.metadata.get('fund_name')},\n"
            f"  inception_date={self.metadata.get('inception_date')},\n"
            f"  num_securities={self.metadata.get('num_securities')},\n"
            f"  holdings.shape={self.holdings.shape}\n"
            f")"
        )


class AmundiETF:
    def __init__(self, titoli_path, nav_path):
        self.titoli_path = titoli_path
        self.nav_path = nav_path
        self.metadata = {}
        self.holdings = pd.DataFrame()
        self.history = pd.DataFrame()
        self._parse_files()

    def _parse_files(self):
        # --- Parse NAV ---
        nav_df = pd.read_csv(self.nav_path, skiprows=26, sep=";", encoding="latin1")
        nav_df = nav_df.iloc[:, 1:3].dropna()
        nav_val = nav_df.iloc[0, 1]
        self.history = nav_val
        self.metadata["curr_value"] = float(nav_val)  
        fund_name, isin = parse_amundi_filename(self.nav_path)
        self.metadata["fund_name"] = fund_name
        self.metadata["isin"] = isin

        # --- Parse Holdings ---
        df = pd.read_csv(self.titoli_path, skiprows=19, sep=";")
        df = df.iloc[:, 1:].dropna()

        # Rename
        df = df.rename(columns={
            "Codice ISIN": "Ticker",
            "Nome": "Name",
            "Settore": "Sector",
            "Peso": "Weight",
            "Paese": "Location",
            "Asset class": "Asset_Class",
            "Valuta": "Currency"
        })

        # Now clean
        df = self._clean_holdings_dataframe(df)
        self.holdings = df


    def _clean_holdings_dataframe(self, df):
        df['Weight'] = (
            df['Weight'].astype(str)
            .str.replace('%', '', regex=False)
            .str.strip()
        )
        df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
        return df[['Ticker', 'Name', 'Sector', 'Asset_Class', 'Weight', 'Location', 'Currency']]

    def get_exposure_by(self, group_by: str) -> pd.DataFrame:
        """
        Returns the percentage weight exposure of the ETF grouped by the specified column.

        Parameters:
            group_by (str): The column name to group by (e.g., 'Location', 'Sector').

        Returns:
            pd.DataFrame: Sorted DataFrame with two columns: [group_by, 'Weight'].
        """
        if group_by not in self.holdings.columns or 'Weight' not in self.holdings.columns:
            return pd.DataFrame(columns=[group_by, 'Weight'])

        grouped = self.holdings.groupby(group_by)['Weight'].sum().reset_index()
        grouped = grouped.sort_values(by='Weight', ascending=False).reset_index(drop=True)
        return grouped

    def __repr__(self):
        return (
            f"AmundiETF(\n"
            f"  fund_name={self.metadata.get('fund_name')},\n"
            f"  isin={self.metadata.get('isin')},\n"
            f"  curr_value={self.metadata.get('curr_value')},\n"
            f"  holdings.shape={self.holdings.shape}\n"
            f")"
        )
