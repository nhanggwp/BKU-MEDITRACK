#!/usr/bin/env python3
"""
TWOSIDES Database Population Script

This script processes the TWOSIDES.csv file and populates the drug_interactions table
in the Supabase database. TWOSIDES is a comprehensive side effect database derived
from FDA Adverse Event Reporting System (FAERS) data.

Usage:
    python populate_twosides.py [--batch-size 1000] [--dry-run]
"""

import asyncio
import pandas as pd
import os
import sys
import argparse
from typing import List, Dict, Any
import hashlib
from tqdm import tqdm

# Add the parent directory to the path to import our services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import SupabaseService
from config.settings import Settings

class TWOSIDESPopulator:
    def __init__(self):
        self.settings = Settings()
        self.supabase = SupabaseService()
        self.processed_combinations = set()
    
    def load_twosides_data(self, file_path: str) -> pd.DataFrame:
        """Load TWOSIDES CSV data"""
        try:
            print(f"Loading TWOSIDES data from: {file_path}")
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} records from TWOSIDES database")
            
            # Display column information
            print("\nAvailable columns:")
            for col in df.columns:
                print(f"  - {col}")
            
            return df
        except Exception as e:
            print(f"Error loading TWOSIDES data: {e}")
            return pd.DataFrame()
    
    def normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name for consistency"""
        if pd.isna(drug_name):
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = str(drug_name).lower().strip()
        
        # Remove common suffixes and prefixes
        suffixes_to_remove = [
            ' tablet', ' tablets', ' capsule', ' capsules',
            ' mg', ' mcg', ' ml', ' g', ' injection',
            ' solution', ' cream', ' ointment', ' gel'
        ]
        
        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        return normalized
    
    def map_severity_from_pvalue(self, p_value: float) -> str:
        """Map p-value to severity level"""
        if pd.isna(p_value):
            return "minor"
        
        try:
            p_val = float(p_value)
            if p_val <= 0.001:
                return "major"
            elif p_val <= 0.01:
                return "moderate"
            else:
                return "minor"
        except (ValueError, TypeError):
            return "minor"
    
    def create_interaction_hash(self, drug1: str, drug2: str) -> str:
        """Create unique hash for drug combination"""
        # Sort drugs to ensure consistent hashing regardless of order
        drugs = sorted([drug1.lower().strip(), drug2.lower().strip()])
        combined = f"{drugs[0]}|{drugs[1]}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def process_twosides_data(self, df: pd.DataFrame, batch_size: int = 1000) -> List[Dict[str, Any]]:
        """Process TWOSIDES data into interaction records"""
        
        interactions = []
        
        # Detect column names (TWOSIDES format may vary)
        drug1_col = None
        drug2_col = None
        side_effect_col = None
        p_value_col = None
        
        # Common column name patterns
        possible_drug1_cols = ['drug_1_name', 'drug1_name', 'drug_1', 'stitch_id1']
        possible_drug2_cols = ['drug_2_name', 'drug2_name', 'drug_2', 'stitch_id2']
        possible_side_effect_cols = ['side_effect_name', 'event_name', 'side_effect', 'event']
        possible_p_value_cols = ['p_value', 'pvalue', 'p_val', 'fisher_p']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in possible_drug1_cols):
                drug1_col = col
            elif any(pattern in col_lower for pattern in possible_drug2_cols):
                drug2_col = col
            elif any(pattern in col_lower for pattern in possible_side_effect_cols):
                side_effect_col = col
            elif any(pattern in col_lower for pattern in possible_p_value_cols):
                p_value_col = col
        
        if not drug1_col or not drug2_col:
            print("Error: Could not identify drug name columns in TWOSIDES data")
            print("Available columns:", list(df.columns))
            return []
        
        print(f"Using columns: drug1='{drug1_col}', drug2='{drug2_col}', side_effect='{side_effect_col}', p_value='{p_value_col}'")
        
        # Process each row
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing TWOSIDES data"):
            try:
                drug1_raw = row[drug1_col]
                drug2_raw = row[drug2_col]
                
                # Skip if either drug name is missing
                if pd.isna(drug1_raw) or pd.isna(drug2_raw):
                    continue
                
                drug1 = self.normalize_drug_name(drug1_raw)
                drug2 = self.normalize_drug_name(drug2_raw)
                
                # Skip if normalization resulted in empty strings
                if not drug1 or not drug2 or drug1 == drug2:
                    continue
                
                # Create unique identifier for this drug combination
                interaction_hash = self.create_interaction_hash(drug1, drug2)
                
                # Skip if we've already processed this combination
                if interaction_hash in self.processed_combinations:
                    continue
                
                self.processed_combinations.add(interaction_hash)
                
                # Extract additional information
                side_effect = ""
                if side_effect_col:
                    side_effect = str(row[side_effect_col]) if not pd.isna(row[side_effect_col]) else ""
                
                p_value = None
                if p_value_col:
                    try:
                        p_value = float(row[p_value_col]) if not pd.isna(row[p_value_col]) else None
                    except (ValueError, TypeError):
                        p_value = None
                
                # Map severity
                severity = self.map_severity_from_pvalue(p_value) if p_value else "minor"
                
                # Create description
                description = f"Potential interaction between {drug1} and {drug2}"
                if side_effect:
                    description += f". Associated side effect: {side_effect}"
                
                interaction = {
                    "drug1_name": drug1,
                    "drug2_name": drug2,
                    "interaction_type": "Drug-Drug Interaction",
                    "severity": severity,
                    "description": description,
                    "frequency_score": p_value if p_value else 1.0
                }
                
                interactions.append(interaction)
                
                # Process in batches
                if len(interactions) >= batch_size:
                    yield interactions
                    interactions = []
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        # Yield remaining interactions
        if interactions:
            yield interactions
    
    async def insert_interactions_batch(self, interactions: List[Dict[str, Any]], dry_run: bool = False) -> int:
        """Insert batch of interactions into database"""
        
        if dry_run:
            print(f"[DRY RUN] Would insert {len(interactions)} interactions")
            return len(interactions)
        
        try:
            # Use upsert to handle duplicates
            response = await self.supabase.client.table('drug_interactions').upsert(
                interactions,
                on_conflict='drug1_name,drug2_name'  # Assuming unique constraint exists
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except Exception as e:
            print(f"Error inserting batch: {e}")
            return 0
    
    async def populate_database(self, csv_path: str, batch_size: int = 1000, dry_run: bool = False):
        """Main method to populate database with TWOSIDES data"""
        
        # Load data
        df = self.load_twosides_data(csv_path)
        if df.empty:
            print("No data to process")
            return
        
        print(f"\nStarting database population...")
        print(f"Batch size: {batch_size}")
        print(f"Dry run: {dry_run}")
        
        total_inserted = 0
        total_processed = 0
        
        # Process and insert data in batches
        for batch_interactions in self.process_twosides_data(df, batch_size):
            inserted_count = await self.insert_interactions_batch(batch_interactions, dry_run)
            total_inserted += inserted_count
            total_processed += len(batch_interactions)
            
            print(f"Processed: {total_processed}, Inserted: {total_inserted}, Unique combinations: {len(self.processed_combinations)}")
        
        print(f"\nPopulation complete!")
        print(f"Total records processed: {total_processed}")
        print(f"Total interactions inserted: {total_inserted}")
        print(f"Unique drug combinations: {len(self.processed_combinations)}")

async def main():
    parser = argparse.ArgumentParser(description="Populate drug interactions database with TWOSIDES data")
    parser.add_argument("--csv-path", default="db-twosides/TWOSIDES.csv", help="Path to TWOSIDES CSV file")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for database insertion")
    parser.add_argument("--dry-run", action="store_true", help="Run without actually inserting data")
    
    args = parser.parse_args()
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_path):
        print(f"Error: TWOSIDES CSV file not found at: {args.csv_path}")
        print("\nPlease download the TWOSIDES database and place it in the specified location.")
        print("TWOSIDES data can be obtained from: http://tatonettilab.org/resources/tatonetti-stm.html")
        return
    
    # Initialize populator
    populator = TWOSIDESPopulator()
    
    try:
        await populator.populate_database(args.csv_path, args.batch_size, args.dry_run)
    except Exception as e:
        print(f"Error during population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if running from correct directory
    if not os.path.exists("services/supabase_service.py"):
        print("Please run this script from the BackEnd directory")
        sys.exit(1)
    
    asyncio.run(main())
