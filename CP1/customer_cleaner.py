import pandas as pd
import numpy as np
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class CustomerCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def standardize_column_names(self):
        self.df.columns = (
            self.df.columns
                .str.replace(r'([a-z0-9])([A-Z])', r'\1_\2', regex=True)
                .str.lower()
        )
        return self.df

    def fix_total_charges(self):
        """Replace blank strings with NaN and convert total_charges to float."""
        #16 try except block to catch any unexpected errors during the cleaning process
        try:
            # Count blank or whitespace-only values
            affected_rows = (
                self.df["total_charges"]
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

            # Replace blank strings with NaN
            self.df["total_charges"] = self.df["total_charges"].replace(
                r"^\s*$",
                np.nan,
                regex=True
            )

            # Convert to numeric
            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            logging.info(
                f"Converted total_charges to float. "
                f"{affected_rows} blank values replaced with NaN."
            )

            return self.df

        except Exception as e:
            logging.error(f"Error while cleaning total_charges: {e}")
            raise


    def normalize_binary_columns(self):
        """
        Convert binary categorical columns:
        Yes -> 1
        No  -> 0
        """
        binary_cols = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        for col in binary_cols:
            self.df[col] = self.df[col].map({
                "Yes": 1,
                "No": 0
            })

        logging.info("Binary columns normalized successfully.")

        return self.df


    def handle_nulls(self):
        """
        Fill missing values in total_charges with monthly_charges.
        This is appropriate for new customers who have tenure = 0.
        """

        # Count missing values before filling
        null_count = self.df["total_charges"].isna().sum()

        # Fill NaN values
        self.df["total_charges"] = self.df["total_charges"].fillna(
            self.df["monthly_charges"]
        )

        logging.info(f"Filled {null_count} missing values in total_charges.")

        return self.df


    def clean(self):
        """
        Execute the complete data cleaning pipeline.
        """

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logging.info("Data cleaning completed successfully.")

        return self.df